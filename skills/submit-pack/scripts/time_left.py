#!/usr/bin/env python3
"""Print the time left to the deadline stored in a project rules file.

Usage: time_left.py [FILE ...] [--deadline ISO] [--now ISO]
       time_left.py --self-test

Reads the first line `hack-kit deadline: <ISO-8601 with offset>` from the given files.
--deadline overrides it. Prints `Xd Yh Zm left`, or `deadline passed`. Exit 1 when no deadline
is found, so a caller never shows an invented one.
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LINE = re.compile(r"hack-kit deadline:\s*(\S+)")


def find(files):
    for f in files:
        p = Path(f)
        if p.is_file():
            m = LINE.search(p.read_text())
            if m:
                return m.group(1)
    return None


def left(deadline, now=None):
    d = datetime.fromisoformat(deadline)
    if d.tzinfo is None:
        raise ValueError("deadline needs a UTC offset")
    secs = int((d - (now or datetime.now(timezone.utc))).total_seconds())
    if secs <= 0:
        return "deadline passed"
    return f"{secs // 86400}d {secs % 86400 // 3600}h {secs % 3600 // 60}m left"


def self_test():
    now = datetime.fromisoformat("2026-10-25T00:00:00+00:00")
    assert left("2026-10-26T05:30:00+05:30", now) == "1d 0h 0m left"
    assert left("2026-10-25T01:30:00+00:00", now) == "0d 1h 30m left"
    assert left("2026-10-24T00:00:00+00:00", now) == "deadline passed"
    try:
        left("2026-10-26T00:00:00", now)
        raise AssertionError
    except ValueError:
        pass
    import tempfile

    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "r.md"
        f.write_text("x\nhack-kit deadline: 2026-10-26T18:00:00+05:30\n")
        assert find([Path(t) / "none.md", f]) == "2026-10-26T18:00:00+05:30"
        assert find([Path(t) / "none.md"]) is None
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    args = sys.argv[1:]
    opts = {}
    for k in ("--deadline", "--now"):
        if k in args:
            i = args.index(k)
            opts[k] = args[i + 1]
            del args[i : i + 2]
    dl = opts.get("--deadline") or find(args)
    if not dl:
        print("no deadline found: ask the user for it, with its timezone")
        sys.exit(1)
    now = datetime.fromisoformat(opts["--now"]) if "--now" in opts else None
    print(left(dl, now))
