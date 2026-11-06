"""Script to collect changed, staged, and untracked files for PR review.

Works cross-platform without external dependencies.
Usage:
    python collect_changes.py [--base main]
"""

import argparse
import subprocess
import sys


def run_git_cmd(args: list[str]) -> str:
    try:
        res = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Collect git changes for PR review")
    parser.add_argument("--base", default="main", help="Base branch to compare against (default: main)")
    args = parser.parse_args()

    current_branch = run_git_cmd(["branch", "--show-current"]) or "HEAD"
    print(f"=== PR Review Diff Collector ===")
    print(f"Current Branch: {current_branch}")
    print(f"Target Base:    {args.base}\n")

    # 1. Uncommitted working tree status
    status = run_git_cmd(["status", "--short"])
    print("--- Working Tree Status (Unstaged & Untracked) ---")
    if status:
        print(status)
    else:
        print("Working tree clean (no uncommitted changes).")
    print()

    # 2. Branch diff against base
    diff_stat = run_git_cmd(["diff", "--stat", f"{args.base}...HEAD"])
    if not diff_stat:
        # Fallback to local diff against base if branch not pushed or no merge-base
        diff_stat = run_git_cmd(["diff", "--stat", args.base])
    
    print(f"--- Changes compared to '{args.base}' ---")
    if diff_stat:
        print(diff_stat)
    else:
        print(f"No committed differences found between '{args.base}' and '{current_branch}'.")
    print()

    # 3. List of modified & untracked files
    name_status = run_git_cmd(["diff", "--name-status", f"{args.base}...HEAD"])
    if not name_status:
        name_status = run_git_cmd(["diff", "--name-status", args.base])

    print("--- Detailed File Summary ---")
    if name_status:
        print(name_status)
    else:
        print("No files modified in branch commits.")


if __name__ == "__main__":
    main()

