from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from bisect import insort
from fnmatch import fnmatch
from statistics import mean
from typing import Any, Callable, Optional, Sequence

import aiofiles

from . import logger


class _SpanInstance:
    def __init__(
        self,
        name: str,
        tid: int,
        ts: float,
        dur: float,
        cat: Optional[str] = None,
        self_dur: Optional[float] = None,
        parent: Optional["_SpanInstance"] = None,
        args: Optional[dict] = None,
    ) -> None:
        self.name = name
        self.tid = tid
        self.ts = ts
        self.dur = dur
        self.cat = cat
        self.args = args or {}

        self.uuid: str = uuid.uuid4().hex

        if self_dur:
            self.self_dur = self_dur
        else:
            self.self_dur = dur

        if parent:
            self.scoped_name = parent.scoped_name + (name,)
        else:
            self.scoped_name = (name,)

    def __eq__(self, other: _SpanInstance) -> bool:
        return other.uuid == self.uuid

    def __hash__(self) -> int:
        return hash(self.uuid)

    # only here due to insort in py<3.10
    def __lt__(self, other: _SpanInstance) -> bool:
        return self.dur > other.dur

    @property
    def depth(self) -> int:
        return len(self.scoped_name) - 1


class _ChromeTraceThread:
    """As in, thread from the trace, not actual thread in current proc"""

    def __init__(self, tid: int, threadname: str):
        self.tid = tid
        self.threadname = threadname
        self.spans: list[_SpanInstance] = []

    def get_total_dur(self) -> float:
        if self.spans:
            return sum(x.dur for x in self.spans if x.depth == 0)
        return 0.0

    def get_span_totals(self) -> Sequence[dict]:
        groups = {}
        for span in self.spans:
            key = (span.name, span.cat, span.args.get("file", "(nofile)"), span.args.get("line", 0))
            groups.setdefault(key, []).append(span.self_dur)

        # generally dirs above 'source' are not interesting
        def _trim_filepath(filepath: str) -> str:
            parts = filepath.split(os.sep)
            try:
                i = parts.index("source")
                return os.sep.join(parts[i + 1 :])
            except ValueError:
                return filepath

        result = []

        for key, self_durs in groups.items():
            fpath = _trim_filepath(key[2])

            result.append(
                {
                    "span_name": key[0],
                    "cat": key[1],
                    "file": fpath,
                    "line": key[3],
                    "file_and_line": f"{fpath}:{key[3]}",
                    "thread": self.threadname,
                    "count": len(self_durs),
                    "self_dur_total": sum(self_durs),
                }
            )

        return result

    def get_span_wall_durs(self) -> dict[str, dict]:
        return self._get_wall_durs(lambda x: x.name)

    def get_cat_wall_durs(self) -> dict[str, dict]:
        return self._get_wall_durs(lambda x: x.cat)

    def _get_wall_durs(self, key_fn: Callable[[_SpanInstance], Any]) -> dict[Any, dict]:
        durs = {}

        def _visit(span, seen):
            if seen is None:
                seen = set()

            key = key_fn(span)
            data = durs.get(key)

            if not data:
                data = durs[key] = {"wall_dur_total": 0.0, "self_dur_total": 0.0, "count": 0}

            data["count"] += 1
            data["self_dur_total"] += span.self_dur

            if key in seen:
                return seen
            else:
                data["wall_dur_total"] += span.dur
                return seen | {key}

        self._visit_depth_first(_visit)
        return durs

    def _visit_depth_first(self, fn_visit: Callable[[_SpanInstance, Any], None]):
        stack = []

        for span in self.spans:
            while stack:
                parent_span = stack[-1][0]
                if span.ts <= (parent_span.ts + parent_span.dur):
                    break

                stack.pop()

            if stack:
                parent_value = stack[-1][1]
            else:
                parent_value = None

            value = fn_visit(span, parent_value)
            stack.append((span, value))

    def _calc_span_instances(self, events: list[dict]):
        # a trick to extract the span hierarchy - iterate over spans in start-time order, and
        # maintain a stack along the way
        #
        stack = []

        for event in sorted(events, key=lambda x: x["ts"]):
            ts = event["ts"]
            name = event["name"]
            dur = event["dur"]
            cat = event.get("cat")
            parent_span = None

            while stack:
                parent_span = stack[-1]
                if ts <= (parent_span.ts + parent_span.dur):
                    parent_span.self_dur -= dur
                    break

                parent_span = None
                stack.pop()

            span = _SpanInstance(
                name=name, tid=self.tid, ts=ts, dur=dur, cat=cat, parent=parent_span, args=event.get("args")
            )

            stack.append(span)
            self.spans.append(span)


class ChromeTrace:
    """Extracts spans from a chrome trace and computes extra properties.

    https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/preview
    """

    @classmethod
    async def create(cls, filepath: str) -> ChromeTrace:
        """Load a trace

        Args:
            filepath (str): Chrome json file to load
        """
        self = cls()
        self.tracethreads = {}
        await self._init(filepath)
        return self

    def copy(self) -> ChromeTrace:
        other = super().__new__(self.__class__)
        other.tids = self.tids.copy()
        other.spans = self.spans.copy()
        return other

    def export(self) -> dict:
        """Export the chrome trace.

        Returns:
            dict: Chrome trace format.
        """
        events = []

        for tid, tracethread in self.tracethreads.items():
            events.append(
                {"name": "thread_name", "ph": "M", "pid": 1, "tid": tid, "args": {"name": tracethread.threadname}}
            )

        for tracethread in self.tracethreads.values():
            for span in tracethread.spans:
                events.append({"name": span.name, "tid": span.tid, "ph": "X", "pid": 1, "ts": span.ts, "dur": span.dur})

        return events

    def get_avg_walltime_per_span(self):
        """Get average walltime per span.

        Recursion does not affect the result.

        Returns:
            Dict of walltime, keyed by span name.
        """
        span_walltimes = {}

        for tracethread in self.tracethreads.values():
            for span in tracethread.spans:
                values = span_walltimes.setdefault(span.name, [])
                values.append(span.dur)

        return dict((k, mean(v)) for k, v in span_walltimes.items())

    def get_span_totals(self) -> Sequence[dict]:
        """Get total self-time spent per span.

        Spans are collapsed into groups where the following attributes are identical:
        * name
        * tid
        * cat
        * args.file
        * args.line

        Example result:

            [
                {
                    "span_name": "my_span_name",
                    "self_dur_total": 104.3,
                    "thread": "main_thread",
                    "cat": "rendering",
                    "file": ".../foo.py",
                    "line": 101,
                    "file_and_line": ".../foo.py:101"
                    "count": 32106
                },
                ...
            ]
        """
        result = []
        for tracethread in self.tracethreads.values():
            result.extend(tracethread.get_span_totals())

        return result

    def get_span_wall_durs(self) -> Sequence[dict]:
        """Get wall duration per span name, per thread.

        This takes recursion into account - if a 10ms span is called recursively 10 times, wall time is still 10ms.

        Example result:

            [
                {
                    "thread": "main_thread",
                    "span_name": "foo",
                    "wall_dur_total": 10354.21,
                    "self_dur_total": 900.1,
                    "count": 7172
                },
                ...
            ]
        """
        result = []
        for tracethread in self.tracethreads.values():
            span_durs = tracethread.get_span_wall_durs()
            for span_name, data in span_durs.items():
                result.append(
                    {
                        "thread": tracethread.threadname,
                        "span_name": span_name,
                        "wall_dur_total": data["wall_dur_total"],
                        "self_dur_total": data["self_dur_total"],
                        "count": data["count"],
                    }
                )

        return result

    def get_cat_wall_durs(self) -> Sequence[dict]:
        """Get wall duration per category, per thread.

        This takes recursion into account - if a 10ms cat span is called recursively 10 times, wall time is still 10ms.

        Example result:

            [
                {
                    "thread": "main_thread",
                    "cat": "rendering",
                    "wall_dur_total": 10354.21,
                    "self_dur_total": 900.1,
                    "count": 7172
                },
                ...
            ]
        """
        result = []
        for tracethread in self.tracethreads.values():
            cat_durs = tracethread.get_cat_wall_durs()
            for cat, data in cat_durs.items():
                result.append(
                    {
                        "thread": tracethread.threadname,
                        "cat": cat,
                        "wall_dur_total": data["wall_dur_total"],
                        "self_dur_total": data["self_dur_total"],
                        "count": data["count"],
                    }
                )

        return result

    async def _init(self, filepath: str) -> None:
        async with aiofiles.open(filepath) as f:
            content = await f.read()

        def _fn():
            raw = json.loads(content)
            self.raw_event_count = len(raw)
            self._extract_tids(raw)
            self._calc_span_instances(raw)

        await asyncio.get_running_loop().run_in_executor(None, _fn)

    def _extract_tids(self, raw: list[dict]) -> None:
        """
        Eg metadata event for threadname:

            {"name":"thread_name","ph":"M","pid":43640,"tid":22004,"args":{"name":"carb.tasking31 (22004)"}}
        """
        for event in raw:
            if event.get("ph") != "M" or event.get("name") != "thread_name":
                continue

            name = event["args"]["name"]
            tid = event["tid"]

            # strip tid out of name so we can make meaningful comparisons in kibana. Do some
            # related string cleanup too
            #
            name = name.replace(str(tid), "")
            name = name.replace("()", "")
            name = name.strip()

            self.tracethreads[tid] = _ChromeTraceThread(tid, name)

    def _calc_span_instances(self, raw: list[dict]) -> None:
        events_per_tid = {}

        for event in raw:
            if event.get("ph") == "X":
                events_per_tid.setdefault(event["tid"], []).append(event)

        for tid, events in events_per_tid.items():
            tracethread = self.tracethreads.get(tid)

            # sometimes tid isn't listed in trace metadata, is this a profiler bug?
            if not tracethread:
                continue

            tracethread._calc_span_instances(events)
