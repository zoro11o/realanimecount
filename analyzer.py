import requests

ANILIST_API = "https://graphql.anilist.co"

RELATION_TYPES = [
    "PREQUEL", "SEQUEL", "PARENT", "CHILD",
    "SIDE_STORY", "ALTERNATIVE", "ADAPTATION"
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
              title { romaji }
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

    response = requests.post(
        ANILIST_API,
        json={"query": query, "variables": {"username": username}}
    )

    data = response.json()

    if "errors" in data:
        return [], "0m"

    media_map = {}
    lists = data["data"]["MediaListCollection"]["lists"]

    # -------------------------
    # Build media map
    # -------------------------
    for anime_list in lists:
        for entry in anime_list["entries"]:

            if entry["status"] not in INCLUDE_STATUSES:
                continue

            media = entry["media"]
            media_id = media["id"]
            title = media["title"]["romaji"]

            duration = media["duration"] or 0
            total_eps = media["episodes"] or 0
            progress = entry["progress"] or 0
            repeat = entry["repeat"] or 0

            # Base episodes watched
            if entry["status"] == "COMPLETED" and total_eps:
                watched_eps = total_eps
            else:
                watched_eps = progress

            # Add rewatch episodes
            if repeat and total_eps:
                watched_eps += repeat * total_eps

            time_spent = watched_eps * duration

            related_ids = [
                edge["node"]["id"]
                for edge in media.get("relations", {}).get("edges", [])
                if edge["relationType"] in RELATION_TYPES
            ]

            media_map[media_id] = {
                "title": title,
                "related_ids": related_ids,
                "time_spent": time_spent,
                "rewatch_count": repeat
            }

    # -------------------------
    # Make relations bidirectional
    # -------------------------
    for media_id, item in media_map.items():
        for related_id in item["related_ids"]:
            if related_id in media_map:
                if media_id not in media_map[related_id]["related_ids"]:
                    media_map[related_id]["related_ids"].append(media_id)

    visited = set()
    franchises = []
    total_watch_minutes = 0

    def dfs(start_id):
        stack = [start_id]
        component = set()

        while stack:
            current = stack.pop()
            if current not in component:
                component.add(current)

                for neighbor in media_map[current]["related_ids"]:
                    if neighbor in media_map and neighbor not in component:
                        stack.append(neighbor)

        return component

    for media_id in media_map:
        if media_id not in visited:
            component = dfs(media_id)
            visited.update(component)

            titles = []
            total_time = 0

            for mid in component:
                item = media_map[mid]
                total_time += item["time_spent"]

                title_display = item["title"]

                # Show rewatch count only if exists
                if item["rewatch_count"] > 0:
                    title_display += f" (Rewatched x{item['rewatch_count']})"

                titles.append({
                    "title": title_display,
                    "time_spent": format_time(item["time_spent"])
                })

            total_watch_minutes += total_time

            titles.sort(key=lambda x: x["title"].lower())

            franchises.append({
                "franchise_name": titles[0]["title"],
                "total_time": format_time(total_time),
                "total_minutes": total_time,
                "titles": titles
            })

    franchises.sort(key=lambda x: x["total_minutes"], reverse=True)

    return franchises, format_time(total_watch_minutes)
