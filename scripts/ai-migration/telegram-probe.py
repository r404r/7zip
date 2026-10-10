#!/usr/bin/env python3
"""Harmless executable used by the Telegram-to-Kanban bootstrap probe.

No credentials, network, archive operations, arguments, or filesystem writes.
Execute as a file so noninteractive Hermes need not approve inline Python.
"""

import sys


if sys.flags.optimize:
    raise SystemExit("FAIL: assertions must be enabled")
assert 2 + 2 == 4
print("PASS: 2 + 2 == 4 (assertions enabled)")
