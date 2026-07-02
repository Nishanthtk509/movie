from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path("", views.user_login, name="login"),
    path("register/", views.Register, name="register"),

    # Home
    path("home/", views.index, name="index"),

    # Movie
    # path("movies/", views.movies, name="movies"),

    # path("series/", views.series, name="series"),

    # path("watch-later/", views.watch_later, name="watch_later"),

    path('search/', views.search_page, name='search_page'),
    path('api/search/', views.api_search, name='api_search'),

    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("watch/<int:movie_id>/", views.play_movie, name="play_movie"),

    # Favorites
    path("favorites/", views.favorites, name="favorites"),
    path(
        "favorite/add/<int:movie_id>/",
        views.add_favorite,
        name="add_favorite",
    ),
    path(
        "favorite/remove/<int:movie_id>/",
        views.remove_favorite,
        name="remove_favorite",
    ),

    # Watch Later
    path("watch-later/", views.watch_later, name="watch_later"),
    path(
        "watch-later/add/<int:movie_id>/",
        views.add_watch_later,
        name="add_watch_later",
    ),
    path(
        "watch-later/remove/<int:movie_id>/",
        views.remove_watch_later,
        name="remove_watch_later",
    ),

    # Watch History
    path("history/", views.watch_history, name="watch_history"),
    path("logout/", views.user_logout, name="user_logout"),
]


