---
aliases: [{{ title }}]
rating: {{ rating|default(0) }}
watched: {{ watched_date|default("") }}
genres: {{ genres|join(', ') }}
jellyfin_id: {{ jellyfin_id }}
{% if series_id %}series_id: {{ series_id }}{% endif %}
---

# {{ title }} ({{ year|default('N/A') }})

## 📺 Quick Links
- [Play in Jellyfin](http://localhost:8096/web/index.html#!/item?id={{ jellyfin_id }})
{% if series_id %}
- [View in Sonarr](http://localhost:8989/series/{{ series_id }})
{% endif %}

## 🎬 My Review
_Add your thoughts here..._
