from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path("", views.user_login, name="login"),
    path("register/", views.Register, name="register"),

    # Home
    path("home/", views.index, name="index"),

    path('search/', views.search_page, name='search_page'),
    path('api/search/', views.api_search, name='api_search'),

    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("watch/<int:movie_id>/", views.play_movie, name="play_movie"),

    # Favorites
    path("favorites/", views.favorites, name="favorites"),
    path("favorite/add/<int:movie_id>/", views.add_favorite, name="add_favorite"),
    path("favorite/remove/<int:movie_id>/", views.remove_favorite, name="remove_favorite"),

    # Watch Later
    path("watch-later/", views.watch_later, name="watch_later"),
    path("watch-later/add/<int:movie_id>/", views.add_watch_later, name="add_watch_later"),
    path("watch-later/remove/<int:movie_id>/", views.remove_watch_later, name="remove_watch_later"),

    # Watch History
    path("history/", views.watch_history, name="watch_history"),
    path("account/", views.account, name="account"),
    path("account/change-password/", views.change_password, name="change_password"),
    path("logout/", views.user_logout, name="user_logout"),

    # admin auth
    path("admin-panel/login/", views.admin_login, name="admin_login"),
    path("admin-panel/logout/", views.admin_logout, name="admin_logout"),
    path("setup-admin/", views.setup_admin, name="setup_admin"),

    # single manage panel
    path("admin-panel/manage/", views.manage_panel, name="manage_panel"),

    path("admin-panel/movies/add/", views.movie_add, name="movie_add"),
    path("admin-panel/movies/<int:movie_id>/edit/", views.movie_edit, name="movie_edit"),
    path("admin-panel/movies/<int:movie_id>/delete/", views.movie_delete, name="movie_delete"),

    path("admin-panel/genres/add/", views.genre_add, name="genre_add"),
    path("admin-panel/genres/<int:genre_id>/edit/", views.genre_edit, name="genre_edit"),
    path("admin-panel/genres/<int:genre_id>/delete/", views.genre_delete, name="genre_delete"),

    path("admin-panel/languages/add/", views.language_add, name="language_add"),
    path("admin-panel/languages/<int:language_id>/edit/", views.language_edit, name="language_edit"),
    path("admin-panel/languages/<int:language_id>/delete/", views.language_delete, name="language_delete"),

    path("admin-panel/users/<int:user_id>/delete/", views.user_delete, name="user_delete"),

]