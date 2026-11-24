#!/usr/bin/env python3
"""Copy entry.txt to the make.fun output directory, after checking it.

The entry is one line, at most 200 characters, about the dumbest thing
my agent did today. This script refuses to ship anything that breaks
that gate, and refuses to overwrite its own source.
"""

import hashlib
import os
import sys
from pathlib import Path

# sha256 of entry.txt as shipped in this repo. Filled in once the line
# is final; the script exits non-zero if the file on disk differs.
EXPECTED_SHA256 = "a4459a4434ba8820302c9512c75ef90651dc0b9a218e4bb5370c326bb68dea18"

MAX_CHARS = 200


def fail(message):
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def main():
    here = Path(__file__).resolve().parent
    source = here / "entry.txt"

    if not source.is_file():
        fail("entry.txt not found next to main.py")

    raw = source.read_bytes()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail("entry.txt is not valid UTF-8")

    lines = text.split("\n")
    if len(lines) > 2 or (len(lines) == 2 and lines[1] != ""):
        fail("entry.txt must be exactly one line")
    line = lines[0]

    if not (1 <= len(line) <= MAX_CHARS):
        fail("entry is %d characters, must be 1-%d" % (len(line), MAX_CHARS))
    if not line.strip():
        fail("entry must not be only whitespace")

    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        fail("entry.txt sha256 mismatch: got %s, expected %s"
             % (digest, EXPECTED_SHA256))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    destination = Path(out_dir) / "entry.txt"
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.resolve() == source.resolve():
        fail("refusing to copy entry.txt onto itself")

    destination.write_bytes(raw)
    print("wrote %s (%d chars, sha256 %s)"
          % (destination, len(line), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
