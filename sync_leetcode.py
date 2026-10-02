"""
LeetCode -> GitHub auto-sync script.
Checks recent Accepted submissions on LeetCode for a given username,
and logs any NEW solves into progress.md, avoiding duplicates.
Commits each new solve separately so the GitHub contribution graph
reflects the actual number of problems solved per day.
"""

import json
import os
import subprocess
import requests
from datetime import datetime

USERNAME = "sakshi0437"
TRACK_FILE = "synced_problems.json"
LOG_FILE = "progress.md"

GRAPHQL_URL = "https://leetcode.com/graphql"

QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    timestamp
  }
}
"""

def fetch_recent_accepted():
    response = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"username": USERNAME, "limit": 20}},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["recentAcSubmissionList"]


def load_synced():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_synced(synced_slugs):
    with open(TRACK_FILE, "w") as f:
        json.dump(sorted(synced_slugs), f, indent=2)


def append_to_log(solve):
    date_str = datetime.fromtimestamp(int(solve["timestamp"])).strftime("%Y-%m-%d %H:%M")
    with open(LOG_FILE, "a") as f:
        f.write(f"- **{solve['title']}** — solved on {date_str}\n")


def git_commit():
    subprocess.run(["git", "add", LOG_FILE, TRACK_FILE], check=True)
    result = subprocess.run(["git", "diff", "--staged", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update progress"], check=True)
        subprocess.run(["git", "push"], check=True)


def main():
    submissions = fetch_recent_accepted()
    already_synced = load_synced()

    # oldest first, so commits land in chronological order
    new_solves = [s for s in submissions if s["titleSlug"] not in already_synced]
    new_solves.sort(key=lambda s: int(s["timestamp"]))

    if not new_solves:
        print("No new solves found. Nothing to commit.")
        return

    for solve in new_solves:
        append_to_log(solve)
        already_synced.add(solve["titleSlug"])
        save_synced(already_synced)
        git_commit()
        print(f"Committed: {solve['title']}")

    print(f"Done. {len(new_solves)} new solve(s) committed separately.")


if __name__ == "__main__":
    main()
