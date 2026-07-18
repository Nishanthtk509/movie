from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_movie_video_key"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE catalog_movie
                ADD COLUMN IF NOT EXISTS video_key varchar(255) NOT NULL DEFAULT '';
            """,
            reverse_sql="""
                ALTER TABLE catalog_movie
                DROP COLUMN IF EXISTS video_key;
            """,
        ),
    ]