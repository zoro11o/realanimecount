# RealAnimeCount

RealAnimeCount is a web app that calculates your actual anime count by grouping related entries (sequels, prequels, side stories, etc.) into single franchises.

It fetches data from your AniList account using your username and processes it to provide a more accurate count of watched anime along with total watch time and re-watches.

It uses AniList data and processes it to give a more accurate representation of how much anime you've watched, along with total watch time.

---
Live on https://realanimecount.onrender.com/

## What it does

- Fetches your anime list from AniList
- Groups connected anime into franchises using their relations
- Counts each franchise once instead of counting every season separately
- Calculates total watch time including rewatches

---

## How to use

1. Enter your AniList username
2. Submit the form
3. View:
   - Total number of unique franchises
   - Total watch time
   - Breakdown of each franchise and its entries

---

## Run locally

```bash
git clone https://github.com/zoro11o/realanimecount.git
cd realanimecount
pip install flask requests
python app.py
```

Open in browser:

```
http://localhost:10000

(or check terminal for the exact port)
```

---
