"""Thin QuantConnect REST API v2 client.

Credentials come only from the environment variables QC_USER_ID and QC_API_TOKEN. They are never
printed, logged, stored or placed in URLs; error messages are scrubbed of both values.
"""
from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests

BASE_URL = "https://www.quantconnect.com/api/v2"
LOG_PAGE = 200      # server maximum lines per backtests/read/log call
ORDER_PAGE = 100    # server maximum orders per backtests/orders/read call
STALL_S = 45 * 60   # no progress for this long = stalled backtest (normal IS runs take 5-10 min)


class QCError(RuntimeError):
    pass


FILLED_STATUSES = (2, 3)   # LEAN OrderStatus: 2 = partially filled, 3 = filled


def incomplete_order(order: dict) -> bool:
    """True if the order is (partially) filled but its fill events have not been delivered yet."""
    if order.get("status") not in FILLED_STATUSES:
        return False
    return not any(ev.get("status") in ("filled", "partiallyFilled") for ev in order.get("events") or [])


class MissingCredentialsError(QCError):
    pass


def auth_headers(user_id: str, token: str, now: Callable[[], float] = time.time) -> tuple[tuple[str, str], dict]:
    """QC v2 auth: basic auth (user_id, sha256("token:timestamp")) plus a Timestamp header."""
    ts = str(int(now()))
    digest = hashlib.sha256(f"{token}:{ts}".encode()).hexdigest()
    return (user_id, digest), {"Timestamp": ts}


@dataclass
class BacktestHandle:
    project_id: int
    backtest_id: str
    compile_id: str


class QCClient:
    def __init__(self, user_id: str | None = None, token: str | None = None,
                 session: requests.Session | None = None, max_retries: int = 5):
        self._user = user_id if user_id is not None else os.environ.get("QC_USER_ID", "")
        self._token = token if token is not None else os.environ.get("QC_API_TOKEN", "")
        if not self._user or not self._token:
            raise MissingCredentialsError("QC_USER_ID / QC_API_TOKEN are not set in the environment.")
        self._http = session or requests.Session()
        self._max_retries = max_retries
        self._org_id: str | None = None

    # ------------------------------------------------------------------ low level
    def _scrub(self, text: str) -> str:
        for secret in (self._token, self._user):
            if secret:
                text = text.replace(secret, "***")
        return text

    def call(self, endpoint: str, **payload: Any) -> dict:
        delay = 2.0
        last: str = ""
        for attempt in range(self._max_retries + 1):
            auth, headers = auth_headers(self._user, self._token)
            try:
                resp = self._http.post(f"{BASE_URL}/{endpoint}", auth=auth, headers=headers,
                                       json=payload, timeout=120)
                if resp.status_code in (429, 500, 502, 503, 504):
                    last = f"HTTP {resp.status_code}"
                else:
                    resp.raise_for_status()
                    data = resp.json()
                    if not data.get("success", False):
                        raise QCError(self._scrub(f"{endpoint} failed: {data.get('errors') or data}"))
                    return data
            except (requests.ConnectionError, requests.Timeout) as exc:
                last = type(exc).__name__
            except requests.HTTPError as exc:
                raise QCError(self._scrub(f"{endpoint}: HTTP {exc.response.status_code}")) from None
            if attempt < self._max_retries:
                time.sleep(delay)
                delay *= 2
        raise QCError(self._scrub(f"{endpoint}: giving up after retries ({last})"))

    # ------------------------------------------------------------------ account
    def authenticate(self) -> bool:
        return bool(self.call("authenticate").get("success"))

    def organization_id(self) -> str:
        if self._org_id is None:
            self._org_id = self.call("account/read")["organizationId"]
        return self._org_id

    def organization(self) -> dict:
        return self.call("organizations/read", organizationId=self.organization_id())["organization"]

    # ------------------------------------------------------------------ projects & files
    def find_or_create_project(self, name: str) -> int:
        for p in self.call("projects/read").get("projects", []):
            if p.get("name") == name:
                return int(p["projectId"])
        return int(self.call("projects/create", name=name, language="Py")["projects"][0]["projectId"])

    def list_files(self, project_id: int) -> list[str]:
        return [f["name"] for f in self.call("files/read", projectId=project_id).get("files", [])]

    def sync_files(self, project_id: int, files: dict[str, str]) -> None:
        """Make the project contain exactly `files` (name -> content)."""
        existing = set(self.list_files(project_id))
        for name, content in files.items():
            if name in existing:
                self.call("files/update", projectId=project_id, name=name, content=content)
            else:
                self.call("files/create", projectId=project_id, name=name, content=content)
        for name in existing - set(files):
            self.call("files/delete", projectId=project_id, name=name)

    def pin_lean_version(self, project_id: int, version_id: int) -> None:
        """Pin the project to an explicit LEAN build (API field `versionId`) and verify it stuck."""
        self.call("projects/update", projectId=project_id, versionId=int(version_id))
        got = self.call("projects/read", projectId=project_id)["projects"][0].get("leanVersionId")
        if int(got) != int(version_id):
            raise QCError(f"LEAN version pin failed: project reports {got}, wanted {version_id}")

    # ------------------------------------------------------------------ compile & backtest
    def compile(self, project_id: int, timeout_s: float = 600) -> str:
        cid = self.call("compile/create", projectId=project_id)["compileId"]
        t0 = time.time()
        while True:
            r = self.call("compile/read", projectId=project_id, compileId=cid)
            if r["state"] == "BuildSuccess":
                return cid
            if r["state"] == "BuildError":
                raise QCError("Build failed: " + " | ".join(r.get("logs", [])[-10:]))
            if time.time() - t0 > timeout_s:
                raise QCError("Compile timed out")
            time.sleep(2)

    def start_backtest(self, project_id: int, compile_id: str, name: str) -> BacktestHandle:
        bt = self.call("backtests/create", projectId=project_id, compileId=compile_id,
                       backtestName=name)["backtest"]
        return BacktestHandle(project_id, bt["backtestId"], compile_id)

    def read_backtest(self, h: BacktestHandle) -> dict:
        return self.call("backtests/read", projectId=h.project_id, backtestId=h.backtest_id)["backtest"]

    def wait_backtest(self, h: BacktestHandle, timeout_s: float = 6 * 3600, poll_s: float = 5,
                      stall_s: float = STALL_S, clock: Callable[[], float] = time.time,
                      sleep: Callable[[float], None] = time.sleep) -> dict:
        """Wait for completion. A backtest whose progress has not moved for `stall_s` is declared
        stalled (E003-06: stuck at 97% for 6 h while occupying the only node) instead of being
        waited on until the 6 h ceiling."""
        t0 = clock()
        last_progress, last_change = None, t0
        while True:
            bt = self.read_backtest(h)
            if bt.get("error") or bt.get("stacktrace"):
                return bt
            # H020 E021-01: QuantConnect may report completed = True while the status is still "In Progress..."
            # (progress 0.999) and the algorithm's end-of-run computation is still running; results are final only
            # when the status is final as well
            if bt.get("completed") and "in progress" not in str(bt.get("status", "")).lower():
                return bt
            now = clock()
            prog = bt.get("progress")
            if prog != last_progress:
                last_progress, last_change = prog, now
            elif now - last_change > stall_s:
                raise QCError(f"Backtest {h.backtest_id} stalled: progress {prog} unchanged for "
                              f"{(now - last_change) / 60:.0f} min (status {bt.get('status')!r})")
            if now - t0 > timeout_s:
                raise QCError(f"Backtest {h.backtest_id} timed out")
            sleep(poll_s)

    def running_backtests(self) -> list[tuple[str, str]]:
        """(project name, backtest name) of every backtest in the account that has not completed.
        The organisation has one backtest node, so any entry here makes a new backtest impossible."""
        out = []
        for p in self.call("projects/read").get("projects", []):
            for b in self.call("backtests/list", projectId=p["projectId"]).get("backtests", []):
                if not b.get("completed"):
                    out.append((p.get("name", ""), b.get("name", "")))
        return out

    # ------------------------------------------------------------------ results
    def read_orders(self, h: BacktestHandle, expected: int | None = None, timeout_s: float = 7200) -> list[dict]:
        """All orders with their events. QC publishes orders and their events asynchronously after
        the backtest completes, so this re-reads until (a) the number of distinct orders equals
        `expected` (QuantConnect's own "Total Orders" statistic) and (b) every filled order carries a
        fill event. An empty or short download is never accepted as complete (E901-02 incident)."""
        t0 = time.time()
        n, missing, last_err = 0, 0, ""
        while True:
            try:
                out = self._read_orders_once(h)
            except QCError as exc:      # E003-04/05: transient "try again later" / HTTP 500 from the
                last_err = str(exc)     # orders endpoint; keep polling inside the window, never accept
                out = None              # a partial download
            if out is not None:
                n = len({o.get("id") for o in out})
                missing = sum(1 for o in out if incomplete_order(o))
                if missing == 0 and (expected is None or n == expected):
                    return out
            if time.time() - t0 > timeout_s:
                raise QCError(f"orders incomplete after {timeout_s:.0f}s: downloaded {n} of {expected} orders, "
                              f"{missing} lack fill events" + (f"; last API error: {last_err}" if last_err else ""))
            time.sleep(15)

    def _read_orders_once(self, h: BacktestHandle) -> list[dict]:
        out: list[dict] = []
        start = 0
        while True:
            r = self.call("backtests/orders/read", projectId=h.project_id, backtestId=h.backtest_id,
                          start=start, end=start + ORDER_PAGE)
            if r.get("status") == "loading":   # the server is still building the order cache
                raise QCError("orders endpoint still loading")
            page = r.get("orders", [])
            out.extend(page)
            total = int(r.get("length", len(out)))
            start += ORDER_PAGE
            if not page or start >= total:
                return out

    def read_statistics(self, h: BacktestHandle, must_have: str = "", timeout_s: float = 300) -> dict:
        """Backtest summary statistics (includes the harness's qr_* keys, D046). Re-reads until
        `must_have` is present or the timeout passes (the server may finalise them after completion)."""
        t0 = time.time()
        while True:
            st = self.read_backtest(h).get("statistics") or {}
            if not must_have or must_have in st or time.time() - t0 > timeout_s:
                return st
            time.sleep(10)

    def read_logs(self, h: BacktestHandle, must_contain: str = "", timeout_s: float = 600) -> list[str]:
        """All log lines; if `must_contain` is given, re-read until some line contains it."""
        t0 = time.time()
        while True:
            out = self._read_logs_once(h)
            if not must_contain or any(must_contain in ln for ln in out):
                return out
            if time.time() - t0 > timeout_s:
                return out   # the caller's integrity checks will flag the missing line
            time.sleep(10)

    def _read_logs_once(self, h: BacktestHandle) -> list[str]:
        out: list[str] = []
        start = 0
        while True:
            r = self.call("backtests/read/log", projectId=h.project_id, backtestId=h.backtest_id,
                          format="json", start=start, end=start + LOG_PAGE, query=" ")
            page = r.get("logs", [])
            out.extend(page)
            total = int(r.get("length", len(out)))
            start += LOG_PAGE
            if not page or start >= total:
                return out

    def read_chart(self, h: BacktestHandle, chart: str, start_ts: int, end_ts: int,
                   count: int = 100_000, min_points: int = 1, timeout_s: float = 900) -> dict[str, list]:
        """Series name -> list of [unix_ts, value, ...] for a custom chart.

        The server builds chart data asynchronously and can first answer with an empty or partial
        chart, so this polls until the longest series has at least `min_points` points."""
        t0 = time.time()
        while True:
            r = self.call("backtests/chart/read", projectId=h.project_id, backtestId=h.backtest_id,
                          name=chart, count=count, start=start_ts, end=end_ts)
            ch = r.get("chart") or {}
            series = {k: s.get("values", []) for k, s in (ch.get("series") or {}).items()}
            if series and max(len(v) for v in series.values()) >= min_points:
                return series
            if time.time() - t0 > timeout_s:
                raise QCError(f"Chart {chart} incomplete after {timeout_s:.0f}s "
                              f"({max((len(v) for v in series.values()), default=0)} of {min_points} points)")
            time.sleep(5)

    def lean_version(self, bt: dict) -> str:
        return (bt.get("serverStatistics") or {}).get("LEAN Version", "unknown")
