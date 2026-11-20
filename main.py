#!/usr/bin/env python3
"""Entry program for the news-image-20261120 bounty.

The front page itself (entry.png) is built by build_page.py in this
repository and ships beside this file. This program only copies that
finished image to the output directory, so the graded run is fully
deterministic and offline: no network access, no third-party packages,
Python standard library only.

Run:  python3 main.py
Writes:  $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png)
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("missing entry.png next to main.py", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
