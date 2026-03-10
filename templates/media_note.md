---
aliases: [{{ title }}]
rating: {{ rating }}
watched: {{ watched_date }}
genres: {{ genres | join(', ') }}
jellyfin_id: {{ jellyfin_id }}
{% if sonarr_id %}sonarr_id: {{ sonarr_id }}{% endif %}
{% if radarr_id %}radarr_id: {{ radarr_id }}{% endif %}
---

# {{ title }} ({{ year }})

## 📺 Quick Links
- [Play in Jellyfin]({{ jellyfin_url }}/web/index.html#!/item?id={{ jellyfin_id }})
{% if sonarr_id %}- [View in Sonarr]({{ sonarr_url }}/series/{{ sonarr_id }}){% endif %}
{% if radarr_id %}- [View in Radarr]({{ radarr_url }}/movie/{{ radarr_id }}){% endif %}

## 🎬 My Review
_Add your thoughts here..._
