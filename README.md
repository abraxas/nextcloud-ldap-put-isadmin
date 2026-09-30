<p align="center">
  <img src="header.png" alt="Abraxas Labs - nextcloud-ldap-put-isadmin" width="100%">
</p>

<p align="center">
  <a href="https://abraxaslabs.tech"><strong>abraxaslabs.tech</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas">github.com/abraxas</a>
  &nbsp;·&nbsp;
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas/nextcloud-ldap-put-isadmin">nextcloud-ldap-put-isadmin</a>
</p>

# nextcloud-ldap-put-isadmin

**Nextcloud Server** `35.0.0` - Nextcloud GmbH

Unpublished Nextcloud source finding: PUT `/cloud/users/{id}` lets a delegated Users admin edit a target unless that target is in the **local** group `admin`. PATCH on the same path correctly uses `isAdmin()`. LDAP-promoted admins are `isAdmin()===true` and often **not** in that local group.

**A bad actor with the helpdesk-style Users job can disable, quota-lock, or delete a real LDAP-promoted instance admin. The newer PATCH API correctly refuses. The older PUT path does not.**

| | |
|---|---|
| ID | Unpublished Nextcloud source finding #3 (no CVE yet) |
| CWE | [CWE-863](https://cwe.mitre.org/data/definitions/863.html) |
| CVSS | **High: 7.2** `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H` (delegated Users admin, not instance admin) |
| Product | [Nextcloud Server](https://github.com/nextcloud/server) |
| Affected | **35.0.0** (`da02f41`) official `nextcloud:35.0.0-apache` plus `user_ldap` |
| Patched | vendor patch - see references |
| Auth | delegated Users admin vs LDAP-promoted admin |
| License | [GNU Affero GPL v3.0](LICENSE) |
| Lab | `127.0.0.1` only |

---

## What an attacker can do

On an LDAP site, you promoted an LDAP group to instance admin (`occ ldap:promote-group`). Those people are real admins (`isAdmin()===true`) but they may **not** sit in the local Nextcloud group named `admin`.

You also gave someone the **Users** settings job (helpdesk). They are not a full instance admin.

That helpdesk user can:

- **Change quota** on the LDAP-promoted admin (lab: PUT 200, PATCH 403)
- **Disable** or **delete** that admin (same `isInGroup` gate on enable/disable/delete/wipe)
- Reset password **if** the LDAP backend allows `canChangePassword()` (often false; do not depend on it)

They cannot do this to someone who is actually in the local `admin` group. They cannot do this on a site with no LDAP-promoted admins. The safer PATCH API already knows the difference.

---

## Advisory (from the source map)

`UsersController::editUser` PUT ~1273-1277 `isInGroup($target, 'admin')`. `editUserMultiField` PATCH ~952-954 `isAdmin($target)`. `Manager::isAdmin()` asks LDAP `IIsAdmin` then local group. Disable/enable/delete/wipe use the PUT-style group check.

---

## Reproduction (authorized lab)

```bash
cd lab
./run.sh
```

Target **only** `http://127.0.0.1:18342` (OpenLDAP on compose DNS `ldap:389`).

Success last line:

```text
SUCCESS NEXTCLOUD-LDAP-PUT-ISADMIN who=delegated-users-admin target=ldapadmin put=200 patch=403 NEXTCLOUD-LDAP-PUT-ISADMIN-WITNESS
```

---

## Lab images

- [`lab/docker-compose.yml`](lab/docker-compose.yml)
- [`lab/Dockerfile`](lab/Dockerfile)
- [`lab/run.sh`](lab/run.sh)
- [`lab/ldap/50-seed.ldif`](lab/ldap/50-seed.ldif)
- [`lab/fixture.php`](lab/fixture.php)

Publish nothing except `127.0.0.1`.

---

## References

- [github.com/nextcloud/server](https://github.com/nextcloud/server) tag [v35.0.0](https://github.com/nextcloud/server/releases/tag/v35.0.0)
- LDAP promote: `occ ldap:promote-group` (PR `#41650`)
- Vendor intake: [hackerone.com/nextcloud](https://hackerone.com/nextcloud). Do **not** open a public GitHub issue.
- Abraxas Labs: [abraxaslabs.tech](https://abraxaslabs.tech) · [github.com/abraxas](https://github.com/abraxas) · [@abraxas_null](https://x.com/abraxas_null)

---

## License

GNU Affero GPL v3.0. See [LICENSE](LICENSE). Loopback lab only. No warranty.
