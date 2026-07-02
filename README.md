# Streamvid

A Django streaming-platform homepage: hero banner, trending/new-release rows, and a
Title/Genre model backing everything through the Django admin.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # to manage titles in /admin/
python manage.py seed_catalog      # optional: adds 7 sample fictional titles
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Structure

- `catalog/models.py` — `Genre` and `Title` models (poster/backdrop images, genres,
  rating, runtime, IMDB-style score, and `is_featured` / `is_trending` / `is_new_release` flags)
- `catalog/views.py` — homepage pulls the featured title for the hero and queries the
  trending / new-release rows
- `catalog/templates/catalog/` — `base.html` (nav + footer shell), `home.html` (hero +
  rows), `title_detail.html`
- `static/css/style.css` — the full design system (dark cinematic theme, violet→orange
  accent gradient, Space Grotesk/Inter type pairing)

## Adding content

Go to `/admin/`, add a few `Genre` entries, then add a `Title`. Check "Featured" on one
title to make it the hero; check "Trending"/"New release" to place others into the
content rows. Poster/backdrop images are optional — titles without an uploaded image
fall back to a generated gradient placeholder so the layout never breaks.

## Note on the reference design

The homepage layout (nav, hero, badge row, thumbnail strip, content rows) is built to
match the mockup you shared. The sample data uses original, fictional titles rather
than the real film and photo in that mockup, since those are copyrighted — swap in
your own catalog via the admin.
