from django.db import models

class Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class Signup(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username


class Genre(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Movie(models.Model):
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=10)

    video_key = models.CharField(max_length=255, default="", blank=True)  # B2 object key, not a Django FileField
    poster = models.ImageField(upload_to="posters/")
    description = models.CharField(max_length=500)

    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name="movies"
    )

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name="movies"
    )

    def __str__(self):
        return self.name
class WatchHistory(models.Model):

    user = models.ForeignKey(
        Signup,
        on_delete=models.CASCADE,
        related_name="watch_history"
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    watched_at = models.DateTimeField(auto_now=True)

    progress = models.PositiveIntegerField(default=0)

    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-watched_at"]
        unique_together = ("user", "movie")


class Favorite(models.Model):

    user = models.ForeignKey(
        Signup,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")

class WatchLater(models.Model):

    user = models.ForeignKey(
        Signup,
        on_delete=models.CASCADE,
        related_name="watch_later"
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")


