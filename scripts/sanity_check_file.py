#!/usr/bin/env python3
import argparse
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['diff', 'ls'], default='diff')
args = parser.parse_args()

ACTUAL_BRANCH = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    stdout=subprocess.PIPE
).stdout.decode().strip()

BRANCH_NAME = os.environ.get("CI_COMMIT_REF_NAME", ACTUAL_BRANCH)
PINK_FILE = "faraday/server/api/modules/reports.py"
BLACK_FILE = "faraday/server/api/modules/jira.py"

mode = args.mode
if mode == "diff":
    child = subprocess.run(
        "git diff --cached --name-status | awk '$1 != \"D\" {print $2 }'",
        shell=True,
        stdout=subprocess.PIPE
    )
else:
    child = subprocess.run(
        ["git", "ls-tree", BRANCH_NAME, "--name-only", "-r"],
        stdout=subprocess.PIPE
    )


def git_diff_intersection(files: set):
    return files.intersection(set(child.stdout.decode().split()))


if __name__ == '__main__':
    print(f"Current branch {ACTUAL_BRANCH} should be equal to {BRANCH_NAME}")
    intersection = set()
    if "white" in BRANCH_NAME:
        intersection = git_diff_intersection({PINK_FILE, BLACK_FILE})
    elif "pink" in BRANCH_NAME:
        intersection = git_diff_intersection({BLACK_FILE})
    assert len(intersection) == 0, f"The {intersection} should not be in " \
                                   f"{BRANCH_NAME}"
    assert child.returncode == 0
