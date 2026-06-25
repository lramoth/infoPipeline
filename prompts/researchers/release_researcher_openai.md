# release_researcher_openai.md

Find direct Bandcamp and Beatport release pages for new underground techno releases from the last 7 days.

Search only:

- Bandcamp
- Beatport

Use search queries focused on:

- `site:bandcamp.com techno EP`
- `site:bandcamp.com hypnotic techno`
- `site:bandcamp.com raw techno`
- `site:bandcamp.com deep techno`
- `site:beatport.com/release techno`
- `site:beatport.com/release hypnotic techno`
- `site:beatport.com/release raw techno`
- `site:beatport.com/release deep techno`
- `Beatport new techno releases`
- `Bandcamp new techno releases`

Return only direct release pages.

Do not return tag pages, artist pages, label pages, charts, playlists, search pages, articles, category pages, or broken links.

Return at least 10 candidate releases when available.

Each item must include:

- title
- url
- summary

The url must be the direct Bandcamp or Beatport release URL for that item.

The summary must be one sentence and include release-date or recent-release evidence.

Return ONLY a JSON array of objects in this exact shape:

[
  {
    "title": "Artist - Release Title",
    "url": "https://...",
    "summary": "One sentence including release-date or recent-release evidence."
  }
]
