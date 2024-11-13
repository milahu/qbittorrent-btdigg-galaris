#!/usr/bin/env python3

import os
import sys
import shlex
import subprocess

if len(sys.argv) == 1:
    print("error: no arguments", file=sys.stderr)
    print("example use: ./test-btdig.py scary movie", file=sys.stderr)
    sys.exit(1)

args = [
    sys.executable, # "python3"
    "nova3/nova2.py",
    "btdig",
    "all",
    *sys.argv[1:],
]

os.environ["DEBUG_NOVA3_ENGINES_BTDIG"] = "1"

print("> " + shlex.join(args))
subprocess.run(args)
