from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import *


# ---------------- CUSTOM SESSION AUTH DECORATOR ----------------

def user_login_required(view_func):
    """
    Use this on all user-facing views that rely on request.session['user_id'].
    Django's built-in @login_required won't work here since we're not using
    Django's authenticate()/login() for regular users.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("user_login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------- ADMIN LOGIN (real Django auth) ----------------

def admin_login(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and user.is_superuser:

            login(request, user)

            return redirect("knowledge")

        error = "Invalid admin credentials"

    return render(
        request,
        "adminlogin.html",
        {
            "error": error
        }
    )


# ---------------- REGISTER ----------------

@never_cache
def Register(request):

    error = ""
    success = ""

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not username or not password or not confirm_password:
            error = "All fields are required."

        elif len(username) < 3:
            error = "Username must be at least 3 characters."

        elif len(password) < 8:
            error = "Password must be at least 8 characters."

        elif password != confirm_password:
            error = "Passwords do not match."

        elif Signup.objects.filter(username=username).exists():
            error = "Username already exists."

        else:
            Signup.objects.create(
                username=username,
                password=password
            )

            return redirect("login")

    return render(
        request,
        "register.html",
        {
            "error": error,
            "success": success
        }
    )


# ---------------- USER LOGIN / LOGOUT ----------------

@never_cache
def user_login(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:

            error = "Please enter username and password."

        else:

            user = Signup.objects.filter(
                username=username
            ).first()

            if user is None:

                error = "Username does not exist."

            elif user.password != password:

                error = "Incorrect password."

            else:

                request.session["user_id"] = user.id
                request.session["username"] = user.username

                return redirect("index")

    return render(
        request,
        "login.html",
        {
            "error": error
        }
    )


@never_cache
def user_logout(request):

    request.session.pop("user_id", None)
    request.session.pop("username", None)

    return redirect("user_login")


def get_logged_in_user(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    return Signup.objects.filter(id=user_id).first()


# ---------------- HOME ----------------

@user_login_required
def index(request):

    movies = Movie.objects.select_related('genre', 'language').order_by('-id')

    hero_movies = movies[:5]
    trending_movies = movies[:12]

    top_language = (
        Language.objects.annotate(count=Count('movies'))
        .order_by('-count')
        .first()
    )
    language_section = {
        'title': top_language.name if top_language else '',
        'movies': movies.filter(language=top_language)[:12] if top_language else [],
    }

    top_genres = Genre.objects.annotate(count=Count('movies')).order_by('-count')[:2]
    genre_sections = [
        {'title': g.name, 'movies': movies.filter(genre=g)[:12]}
        for g in top_genres
    ]

    context = {
        'movies': movies,
        'hero_movies': hero_movies,
        'trending_movies': trending_movies,
        'language_section': language_section,
        'genre_sections': genre_sections,
    }
    return render(request, 'index.html', context)


# ---------------- MOVIE DETAILS ----------------

@user_login_required
def movie_detail(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    favorites = Favorite.objects.filter(
        user_id=request.session["user_id"]
    ).values_list("movie_id", flat=True)

    watch_later = WatchLater.objects.filter(
        user_id=request.session["user_id"]
    ).values_list("movie_id", flat=True)

    return render(
        request,
        "movie_detail.html",
        {
            "movie": movie,
            "favorites": favorites,
            "watch_later": watch_later,
        },
    )


# ---------------- PLAY MOVIE ----------------

@user_login_required
def play_movie(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    WatchHistory.objects.get_or_create(
        user_id=request.session["user_id"],
        movie=movie
    )

    favorites = Favorite.objects.filter(
        user_id=request.session["user_id"]
    ).values_list("movie_id", flat=True)

    watch_later = WatchLater.objects.filter(
        user_id=request.session["user_id"]
    ).values_list("movie_id", flat=True)

    related_movies = Movie.objects.filter(
        genre=movie.genre
    ).exclude(
        id=movie.id
    )[:8]

    return render(
        request,
        "player.html",
        {
            "movie": movie,
            "favorites": favorites,
            "watch_later": watch_later,
            "related_movies": related_movies,
        },
    )


# ---------------- FAVORITES ----------------

@user_login_required
def add_favorite(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    Favorite.objects.get_or_create(
        user_id=request.session["user_id"],
        movie=movie,
    )

    return redirect(request.META.get("HTTP_REFERER", "index"))


@user_login_required
def remove_favorite(request, movie_id):

    Favorite.objects.filter(
        user_id=request.session["user_id"],
        movie_id=movie_id,
    ).delete()

    return redirect(request.META.get("HTTP_REFERER", "favorites"))


@user_login_required
def favorites(request):

    favorites = Favorite.objects.filter(
        user_id=request.session["user_id"]
    ).select_related("movie")

    return render(request, "favorites.html", {"favorites": favorites})


# ---------------- WATCH LATER ----------------

@user_login_required
def add_watch_later(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    WatchLater.objects.get_or_create(
        user_id=request.session["user_id"],
        movie=movie,
    )

    return redirect(request.META.get("HTTP_REFERER", "index"))


@user_login_required
def remove_watch_later(request, movie_id):

    WatchLater.objects.filter(
        user_id=request.session["user_id"],
        movie_id=movie_id,
    ).delete()

    return redirect(request.META.get("HTTP_REFERER", "watch_later"))


@user_login_required
def watch_later(request):

    movies = WatchLater.objects.filter(
        user_id=request.session["user_id"]
    ).select_related("movie")

    return render(request, "watchlater.html", {"movies": movies})


@user_login_required
def watch_history(request):

    history = WatchHistory.objects.filter(
        user_id=request.session["user_id"]
    ).select_related("movie")

    return render(request, "history.html", {"history": history})


# ---------------- SEARCH ----------------

@user_login_required
def search_page(request):

    initial_movies = Movie.objects.select_related('genre', 'language').order_by('-id')[:20]

    context = {
        'genres': Genre.objects.all(),
        'languages': Language.objects.all(),
        'initial_movies': initial_movies,
    }
    return render(request, 'search.html', context)


@user_login_required
def api_search(request):

    q = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    language = request.GET.get('language', '').strip()
    sort = request.GET.get('sort', 'relevance')

    movies = Movie.objects.select_related('genre', 'language')

    if len(q) >= 2:
        movies = movies.filter(Q(name__icontains=q) | Q(genre__name__icontains=q))

    if genre:
        movies = movies.filter(genre__name=genre)

    if language:
        movies = movies.filter(language__name=language)

    if sort == 'name_asc':
        movies = movies.order_by('name')
    elif sort == 'name_desc':
        movies = movies.order_by('-name')
    elif sort == 'newest':
        movies = movies.order_by('-id')

    movies = movies.distinct()[:40]

    data = [
        {
            "id": m.id,
            "name": m.name,
            "poster": m.poster.url if m.poster and hasattr(m.poster, 'url') else "",
            "genre": m.genre.name if m.genre else "",
            "language": m.language.name if m.language else "",
        }
        for m in movies
    ]

    return JsonResponse(data, safe=False)