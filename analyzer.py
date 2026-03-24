import requests
from collections import defaultdict

ANILIST_API = "https://graphql.anilist.co"

RELATION_TYPES = [
    "PREQUEL", "SEQUEL", "PARENT", "CHILD",
    "SIDE_STORY", "ALTERNATIVE", "ADAPTATION",
    "SPIN_OFF", "SUMMARY"
]

INCLUDE_STATUSES = ["CURRENT", "COMPLETED", "DROPPED", "PAUSED"]


def format_time(minutes):
    if minutes <= 0:
        return "0m"

    days = minutes // (60 * 24)
    hours = (minutes % (60 * 24)) // 60
    mins = minutes % 60

    parts = []
    if days > 0:
        parts.append(f"{int(days)}d")
    if hours > 0:
        parts.append(f"{int(hours)}h")
    if mins > 0:
        parts.append(f"{int(mins)}m")

    return " ".join(parts)


def get_unique_franchises(username):

    query = """
    query ($username: String) {
      MediaListCollection(userName: $username, type: ANIME) {
        lists {
          entries {
            status
            progress
            repeat
            media {
              id
              title {
                romaji
                english
              }
              format
              startDate { year }
              episodes
              duration
              relations {
                edges {
                  relationType
                  node { id }
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            ANILIST_API,
            json={"query": query, "variables": {"username": username}},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timed out for user: {username}")
        return [], "0m"
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e}")
        return [], "0m"
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return [], "0m"
    except ValueError:
        print("[ERROR] Failed to parse JSON response")
        return [], "0m"

    if "errors" in data:
        print(f"[ERROR] AniList API errors: {data['errors']}")
        return [], "0m"

    # Safety check for unexpected response structure
    try:
        lists = data["data"]["MediaListCollection"]["lists"]
    except (KeyError, TypeError):
        print("[ERROR] Unexpected response structure from AniList")
        return [], "0m"

    media_map = {}               # watched anime only
    full_graph = defaultdict(set)  # full connectivity graph

    # -------------------------
    # Build watched media_map + full_graph
    # -------------------------
    for anime_list in lists:
        for entry in anime_list["entries"]:

            if entry["status"] not in INCLUDE_STATUSES:
                continue

            media = entry["media"]
            media_id = media["id"]

            title_data = media["title"]
            title = title_data.get("english") or title_data.get("romaji") or "Unknown"

            duration = media.get("duration") or 0
            total_eps = media.get("episodes") or 0
            progress = entry.get("progress") or 0
            repeat = entry.get("repeat") or 0

            # Episodes watched
            if entry["status"] == "COMPLETED" and total_eps:
                watched_eps = total_eps
            else:
                watched_eps = progress

            if repeat and total_eps:
                watched_eps += repeat * total_eps

            time_spent = watched_eps * duration

            media_map[media_id] = {
                "title": title,
                "time_spent": time_spent,
                "rewatch_count": repeat,
                "format": media.get("format"),
                "start_year": media.get("startDate", {}).get("year")
            }

            # Add ALL relations to full graph (even if not watched)
            for edge in media.get("relations", {}).get("edges", []):
                if edge.get("relationType") in RELATION_TYPES:
                    related_id = edge["node"]["id"]
                    full_graph[media_id].add(related_id)
                    full_graph[related_id].add(media_id)

    visited = set()
    franchises = []
    total_watch_minutes = 0

    # -------------------------
    # DFS using FULL graph
    # -------------------------
    def dfs(start_id):
        stack = [start_id]
        component = set()

        while stack:
            current = stack.pop()
            if current not in component:
                component.add(current)
                for neighbor in full_graph[current]:
                    if neighbor not in component:
                        stack.append(neighbor)

        return component

    # Only start DFS from watched anime
    for media_id in media_map:

        if media_id not in visited:

            component = dfs(media_id)

            # Mark all nodes visited (including bridges)
            visited.update(component)

            # Filter to watched anime only
            watched_component = [
                mid for mid in component if mid in media_map
            ]

            if not watched_component:
                continue

            titles = []
            total_time = 0

            for mid in watched_component:
                item = media_map[mid]
                total_time += item["time_spent"]

                title_display = item["title"]
                if item["rewatch_count"] > 0:
                    title_display += f" (Rewatched x{item['rewatch_count']})"

                titles.append({
                    "title": title_display,
                    "time_spent": format_time(item["time_spent"]),
                    "format": item.get("format"),
                    "start_year": item.get("start_year")
                })

            total_watch_minutes += total_time

            titles.sort(key=lambda x: x["title"].lower())

            # Choose best anchor (oldest TV preferred)
            main_entry = sorted(
                titles,
                key=lambda x: (
                    x.get("format") != "TV",
                    x.get("start_year") or 9999
                )
            )[0]

            franchises.append({
                "franchise_name": main_entry["title"],
                "total_time": format_time(total_time),
                "total_minutes": total_time,
                "titles": titles
            })

    franchises.sort(key=lambda x: x["total_minutes"], reverse=True)

    return franchises, format_time(total_watch_minutes)
