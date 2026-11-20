#!/usr/bin/env python3
"""Copy the composed front page to the output directory.

Stdlib only, no network. The image is verified against its SHA-256
before copying, so every run writes byte-identical output.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "entry.png")
SHA256 = "816cd00149c45a30a34eed970249ab0f780e80c10d3841cf30fd1e273cf13ac5"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    with open(SRC, "rb") as f:
        data = f.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256:
        print(f"entry.png hash mismatch: {digest} != {SHA256}", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    print(f"wrote {dst} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
