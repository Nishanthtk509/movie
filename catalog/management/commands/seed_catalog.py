from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Genre, Title


SAMPLE_TITLES = [
    {
        "name": "Silent Horizon",
        "tagline": "One driver. One night. No way back.",
        "synopsis": "A getaway driver with a code of silence takes one last job across a city that "
                     "refuses to let him leave clean.",
        "kind": "movie",
        "genres": ["Action", "Crime", "Thriller"],
        "release_year": 2024,
        "runtime_minutes": 118,
        "content_rating": "R",
        "imdb_score": 7.9,
        "is_featured": True,
        "is_trending": True,
    },
    {
        "name": "Paper Moons",
        "tagline": "Every family keeps a secret worth telling.",
        "synopsis": "Three estranged siblings return home for their father's funeral and uncover a "
                     "decades-old promise that changes everything they thought they knew.",
        "kind": "movie",
        "genres": ["Drama"],
        "release_year": 2023,
        "runtime_minutes": 104,
        "content_rating": "PG-13",
        "imdb_score": 7.4,
        "is_trending": True,
        "is_new_release": True,
    },
    {
        "name": "The Long Static",
        "tagline": "The signal is not the only thing listening.",
        "synopsis": "A radio astronomer intercepts a pattern that shouldn't exist and must decide "
                     "who else deserves to know.",
        "kind": "series",
        "genres": ["Sci-Fi", "Mystery", "Thriller"],
        "release_year": 2025,
        "runtime_minutes": 48,
        "content_rating": "TV-MA",
        "imdb_score": 8.3,
        "is_trending": True,
        "is_new_release": True,
    },
    {
        "name": "Copper & Rust",
        "tagline": "Some towns run on more than electricity.",
        "synopsis": "A young engineer arrives in a dying mill town and finds the machines are the "
                     "least mysterious thing about it.",
        "kind": "movie",
        "genres": ["Drama", "Mystery"],
        "release_year": 2022,
        "runtime_minutes": 96,
        "content_rating": "PG-13",
        "imdb_score": 6.8,
        "is_new_release": True,
    },
    {
        "name": "Kite Season",
        "tagline": "The sky doesn't forget who let go first.",
        "synopsis": "Childhood best friends reunite for one final summer festival before the coast "
                     "they grew up on disappears for good.",
        "kind": "movie",
        "genres": ["Drama", "Romance"],
        "release_year": 2021,
        "runtime_minutes": 101,
        "content_rating": "PG",
        "imdb_score": 7.1,
    },
    {
        "name": "Ironback Ridge",
        "tagline": "The mountain always collects its due.",
        "synopsis": "A search-and-rescue team races a storm to find survivors of a crash on the "
                     "region's most unforgiving peak.",
        "kind": "movie",
        "genres": ["Action", "Adventure"],
        "release_year": 2024,
        "runtime_minutes": 112,
        "content_rating": "PG-13",
        "imdb_score": 7.6,
        "is_trending": True,
    },
    {
        "name": "Nightshift Diaries",
        "tagline": "Everyone has a story between 2 and 4 a.m.",
        "synopsis": "An anthology series following the strangers who cross paths at an all-night "
                     "diner on the edge of downtown.",
        "kind": "series",
        "genres": ["Drama", "Comedy"],
        "release_year": 2025,
        "runtime_minutes": 32,
        "content_rating": "TV-MA",
        "imdb_score": 7.8,
        "is_new_release": True,
    },
]


class Command(BaseCommand):
    help = "Seed the catalog with sample fictional titles for development."

    def handle(self, *args, **options):
        created_count = 0
        for entry in SAMPLE_TITLES:
            genre_names = entry.pop("genres")
            slug = slugify(entry["name"])
            title, created = Title.objects.update_or_create(
                slug=slug, defaults={**entry, "slug": slug}
            )
            genre_objs = []
            for gname in genre_names:
                genre, _ = Genre.objects.get_or_create(name=gname, defaults={"slug": slugify(gname)})
                genre_objs.append(genre)
            title.genres.set(genre_objs)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded catalog: {created_count} new titles, {len(SAMPLE_TITLES)} total processed."
        ))
