#!/usr/bin/env python3
"""Copy the entry image to the output directory.

The front page (entry.png) is drawn by draw.py in this repository; this
program is the entrypoint the grader runs. It copies the image byte for
byte and verifies the copy, so two runs write identical bytes.
"""
import hashlib
import os
import shutil
import sys

EXPECTED_SHA256 = "87c3e0e04fb363267bd36c5ed8c4f717b35d6c17b038375498b2587ef7a858ca"
EXPECTED_SIZE = 160727


def sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    # Fail early if the bundled image is not the one this entry was built from.
    if os.path.getsize(src) != EXPECTED_SIZE or sha256_of(src) != EXPECTED_SHA256:
        print("source image does not match the expected entry.png",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as f:
        data = f.read()
    size = len(data)
    sha = hashlib.sha256(data).hexdigest()
    if size != EXPECTED_SIZE or sha != EXPECTED_SHA256:
        print(f"verification failed: size={size} sha256={sha}", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({size} bytes, sha256 {sha})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
