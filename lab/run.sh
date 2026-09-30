#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-nextcloud-ldap-put-isadmin}"
export NC_URL="${NC_URL:-http://127.0.0.1:18342}"
export NC_ADMIN_USER="${NC_ADMIN_USER:-admin}"
export NC_ADMIN_PASSWORD="${NC_ADMIN_PASSWORD:-LabAdmin35!}"
export NC_HELPDESK_USER="${NC_HELPDESK_USER:-helpdesk}"
export NC_HELPDESK_PASSWORD="${NC_HELPDESK_PASSWORD:-LabHelpdesk35!}"
export NC_LDAP_UID="${NC_LDAP_UID:-ldapadmin}"
export NC_LDAP_PASSWORD="${NC_LDAP_PASSWORD:-LabLdapAdmin35!}"
export NC_LDAP_GROUP="${NC_LDAP_GROUP:-ncadmins}"
WITNESS="NEXTCLOUD-LDAP-PUT-ISADMIN-WITNESS"
chmod +x poc.py

occ() {
  docker compose exec -T -u www-data nextcloud php occ "$@"
}

occ_pass() {
  local pass="$1"
  shift
  docker compose exec -T -u www-data -e OC_PASS="${pass}" nextcloud php occ "$@"
}

down() {
  echo "== docker compose down -v =="
  docker compose down -v --remove-orphans || true
}

fail_seed() {
  echo "FAIL NEXTCLOUD-LDAP-PUT-ISADMIN $*" | tee poc-last-run.txt
  docker compose logs --tail=80 nextcloud ldap || true
  down
  exit 1
}

echo "== docker compose down (clean) =="
docker compose down -v --remove-orphans || true

echo "== docker compose up (loopback :18342/:18343) =="
up_ok=0
for attempt in $(seq 1 8); do
  if docker compose up -d; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=$attempt"
  sleep 12
done
if [[ "$up_ok" != 1 ]]; then
  fail_seed "docker compose up"
fi

echo "== wait for OpenLDAP seed =="
ldap_ok=0
for i in $(seq 1 60); do
  if docker compose exec -T ldap ldapsearch -x -H ldap://127.0.0.1:389 \
    -D cn=admin,dc=lab,dc=invalid -w LabLdapAdmin35! \
    -b uid=ldapadmin,ou=users,dc=lab,dc=invalid -s base dn >/dev/null 2>&1; then
    echo "IOC ldap-up i=$i ldapadmin-dn-ok"
    ldap_ok=1
    break
  fi
  echo "IOC ldap-wait i=$i"
  sleep 3
done
if [[ "$ldap_ok" != 1 ]]; then
  fail_seed "openldap seed not ready"
fi

echo "== wait for status.php installed=true =="
ok=0
for i in $(seq 1 120); do
  body="$(curl -sS --max-time 8 "${NC_URL}/status.php" || true)"
  echo "IOC wait i=$i status=${body}"
  if echo "$body" | grep -q '"installed":true'; then
    echo "IOC nextcloud-up installed=true"
    ok=1
    break
  fi
  sleep 5
done
if [[ "$ok" != 1 ]]; then
  fail_seed "status.php not installed"
fi

echo "== seed occ / LDAP =="
seed_ok=0
for attempt in $(seq 1 20); do
  if occ status; then
    seed_ok=1
    break
  fi
  echo "IOC occ-wait attempt=$attempt"
  sleep 5
done
if [[ "$seed_ok" != 1 ]]; then
  fail_seed "occ not ready"
fi

if ! docker compose exec -T nextcloud php -m | grep -qi '^ldap$'; then
  fail_seed "php-ldap missing"
fi

occ config:system:set overwrite.cli.url --value="${NC_URL}"
occ config:system:set auth.bruteforce.protection.enabled --value=false --type=boolean || true
occ app:enable user_ldap

prefix="$(occ ldap:create-empty-config --only-print-prefix | tr -d '\r\n[:space:]')"
if [[ -z "$prefix" ]]; then
  fail_seed "ldap:create-empty-config empty prefix"
fi
echo "IOC ldap-prefix=${prefix}"

occ ldap:set-config "$prefix" ldapHost ldap
occ ldap:set-config "$prefix" ldapPort 389
occ ldap:set-config "$prefix" ldapAgentName 'cn=admin,dc=lab,dc=invalid'
occ ldap:set-config "$prefix" ldapAgentPassword LabLdapAdmin35!
occ ldap:set-config "$prefix" ldapBase 'dc=lab,dc=invalid'
occ ldap:set-config "$prefix" ldapBaseUsers 'ou=users,dc=lab,dc=invalid'
occ ldap:set-config "$prefix" ldapBaseGroups 'ou=groups,dc=lab,dc=invalid'
occ ldap:set-config "$prefix" ldapTLS 0
occ ldap:set-config "$prefix" ldapUserDisplayName cn
occ ldap:set-config "$prefix" ldapUserFilter '(objectClass=inetOrgPerson)'
occ ldap:set-config "$prefix" ldapLoginFilter '(&(objectClass=inetOrgPerson)(uid=%uid))'
occ ldap:set-config "$prefix" ldapLoginFilterUsername 1
occ ldap:set-config "$prefix" ldapGroupDisplayName cn
occ ldap:set-config "$prefix" ldapGroupFilter '(objectClass=posixGroup)'
occ ldap:set-config "$prefix" ldapGroupMemberAssocAttr memberUid
occ ldap:set-config "$prefix" ldapEmailAttribute mail
occ ldap:set-config "$prefix" ldapExpertUsernameAttr uid
occ ldap:set-config "$prefix" ldapExpertUUIDUserAttr uid
occ ldap:set-config "$prefix" ldapExpertUUIDGroupAttr cn
occ ldap:set-config "$prefix" hasMemberOfFilterSupport 0
occ ldap:set-config "$prefix" useMemberOfToDetectMembership 0
occ ldap:set-config "$prefix" ldapCacheTTL 0
occ ldap:set-config "$prefix" ldapConfigurationActive 1

test_ok=0
for attempt in $(seq 1 15); do
  if occ ldap:test-config "$prefix" | tee /dev/stderr | grep -q 'configuration is valid'; then
    test_ok=1
    break
  fi
  echo "IOC ldap-test-retry attempt=$attempt"
  sleep 3
done
if [[ "$test_ok" != 1 ]]; then
  occ ldap:show-config "$prefix" || true
  fail_seed "ldap:test-config failed"
fi

occ ldap:search ldapadmin || true
occ ldap:search --group ncadmins || true
occ ldap:check-user ldapadmin || true
occ ldap:check-group ncadmins --update || true

promote_ok=0
for attempt in $(seq 1 10); do
  if occ ldap:promote-group --yes ncadmins | tee /dev/stderr | grep -qiE 'promoted|already promoted'; then
    promote_ok=1
    break
  fi
  echo "IOC promote-retry attempt=$attempt"
  occ ldap:search --group ncadmins || true
  occ ldap:check-group ncadmins --update || true
  sleep 3
done
if [[ "$promote_ok" != 1 ]]; then
  occ group:list --output=json || true
  occ ldap:show-config "$prefix" || true
  fail_seed "ldap:promote-group failed (LDAP never promoted)"
fi

occ group:add helpdesk || true
occ_pass "${NC_HELPDESK_PASSWORD}" user:add --password-from-env --display-name=helpdesk -g helpdesk "${NC_HELPDESK_USER}" || true
occ group:adduser helpdesk "${NC_HELPDESK_USER}" || true
occ admin-delegation:add 'OCA\Settings\Settings\Admin\Users' helpdesk || true
occ user:info "${NC_HELPDESK_USER}" || true
occ user:info "${NC_LDAP_UID}" || true
occ group:list --output=json || true
occ ldap:show-config "$prefix" || true
occ admin-delegation:show || true

echo "== fixture isAdmin / local-admin-group =="
docker compose cp fixture.php nextcloud:/tmp/nc-ldap-put-isadmin-fixture.php
fixture="$(docker compose exec -T -u www-data \
  -e NC_LDAP_UID="${NC_LDAP_UID}" \
  -e NC_HELPDESK_USER="${NC_HELPDESK_USER}" \
  -w /var/www/html nextcloud php /tmp/nc-ldap-put-isadmin-fixture.php || true)"
echo "IOC fixture=${fixture}"
echo "$fixture" | grep -q '"target_isAdmin":true' || fail_seed "target isAdmin not true (LDAP never promoted)"
echo "$fixture" | grep -q '"target_isInGroupAdmin":false' || fail_seed "target is in local admin group (wrong fixture)"
echo "$fixture" | grep -q '"actor_isDelegatedAdmin":true' || fail_seed "helpdesk isDelegatedAdmin not true"
echo "$fixture" | grep -q '"actor_isInGroupAdmin":false' || fail_seed "helpdesk is in local admin group (wrong fixture)"

echo "== poc.py =="
set +e
python3 poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e
if [[ "$rc" != 0 ]]; then
  echo "== nextcloud/ldap logs (tail) ==" | tee -a poc-last-run.txt
  docker compose logs --tail=120 nextcloud ldap | tee -a poc-last-run.txt || true
  echo "== occ user:info ==" | tee -a poc-last-run.txt
  occ user:info "${NC_LDAP_UID}" | tee -a poc-last-run.txt || true
  occ user:info "${NC_HELPDESK_USER}" | tee -a poc-last-run.txt || true
fi
down
exit "$rc"
