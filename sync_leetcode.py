"""
LeetCode -> GitHub auto-sync script.
Checks recent Accepted submissions on LeetCode for a given username,
and logs any NEW solves into progress.md, avoiding duplicates.
"""

import json
import os
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


def append_to_log(new_solves):
    with open(LOG_FILE, "a") as f:
        for solve in new_solves:
            date_str = datetime.fromtimestamp(int(solve["timestamp"])).strftime("%Y-%m-%d %H:%M")
            f.write(f"- **{solve['title']}** — solved on {date_str}\n")


def main():
    submissions = fetch_recent_accepted()
    already_synced = load_synced()

    new_solves = [s for s in submissions if s["titleSlug"] not in already_synced]

    if not new_solves:
        print("No new solves found. Nothing to commit.")
        return

    append_to_log(new_solves)

    for s in new_solves:
        already_synced.add(s["titleSlug"])
    save_synced(already_synced)

    print(f"Logged {len(new_solves)} new solve(s).")


if __name__ == "__main__":
    main()