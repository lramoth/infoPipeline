# release_researcher_openai.md

Find direct Bandcamp and Beatport release pages for new underground techno releases from the last 7 days.

Search only:

- Bandcamp

Use search queries focused on:

- https://bandcamp.com/discover/hypnotic-techno+techno.?t=today

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
