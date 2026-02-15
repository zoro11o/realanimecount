= RealAnimeCount

RealAnimeCount recalculates your true anime count by grouping all related seasons, sequels, and side stories into single franchises instead of counting them separately.

Unlike AniList, which counts every season as a separate entry, RealAnimeCount merges connected anime into unified franchise clusters.

= What It Does

Connects to the AniList GraphQL API

Groups anime by franchise using relation graphs

Uses DFS traversal to detect connected components

Counts one franchise as one anime

Calculates total watch time

Includes partial watches (Current, Dropped, Paused)

Includes rewatches

Displays clean, franchise-based breakdown

= Why It Exists

AniList inflates anime totals by counting:

Season 1

Season 2

Final Season

OVAs

Side stories

as separate anime.

RealAnimeCount fixes that.

= Tech Stack

Python

Flask

GraphQL (AniList API)

DFS Graph Traversal

HTML (Jinja templating)