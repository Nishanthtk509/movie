import logging
from functools import wraps

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.contrib import messages

from .models import *

logger = logging.getLogger(__name__)


# ==================== SESSION DECORATORS ====================

def user_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_id"):
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== ONE-TIME ADMIN SETUP ====================

def setup_admin(request):

    key = request.GET.get("key")
    username = request.GET.get("username")
    password = request.GET.get("password")

    if key != settings.ADMIN_SETUP_SECRET:
        return HttpResponse("Invalid or missing key.", status=403)

    if Admin.objects.exists():
        return HttpResponse("An admin already exists. Setup is locked.", status=403)

    if not username or not password:
        return HttpResponse("Provide ?username=...&password=... in the URL.", status=400)

    if len(password) < 8:
        return HttpResponse("Password must be at least 8 characters.", status=400)

    Admin.objects.create(username=username, password=password)

    return HttpResponse(f"Admin '{username}' created successfully. You can now log in at /admin-panel/login/.")


# ==================== ADMIN LOGIN / LOGOUT ====================

@never_cache
def admin_login(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            error = "Please enter username and password."
        else:
            admin = Admin.objects.filter(username=username).first()

            if admin is None:
                error = "Invalid admin credentials."
            elif admin.password != password:
                error = "Invalid admin credentials."
            else:
                request.session["admin_id"] = admin.id
                request.session["admin_username"] = admin.username
                return redirect("manage_panel")

    return render(request, "adminlogin.html", {"error": error})


@never_cache
def admin_logout(request):
    request.session.pop("admin_id", None)
    request.session.pop("admin_username", None)
    return redirect("admin_login")


# ==================== REGISTER ====================

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
            Signup.objects.create(username=username, password=password)
            return redirect("login")

    return render(request, "register.html", {"error": error, "success": success})


# ==================== USER LOGIN / LOGOUT ====================

@never_cache
def user_login(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            error = "Please enter username and password."
        else:
            user = Signup.objects.filter(username=username).first()

            if user is None:
                error = "Username does not exist."
            elif user.password != password:
                error = "Incorrect password."
            else:
                request.session["user_id"] = user.id
                request.session["username"] = user.username
                return redirect("index")

    return render(request, "login.html", {"error": error})


@never_cache
def user_logout(request):
    request.session.pop("user_id", None)
    request.session.pop("username", None)
    return redirect("login")


@user_login_required
def account(request):
    return render(request, "account.html", {})


@user_login_required
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = Signup.objects.filter(id=request.session["user_id"]).first()

        if user.password != current_password:
            return render(request, "account.html", {"error": "Current password is incorrect."})
        elif new_password != confirm_password:
            return render(request, "account.html", {"error": "New passwords do not match."})
        elif not new_password:
            return render(request, "account.html", {"error": "New password cannot be empty."})
        else:
            user.password = new_password
            user.save()
            return render(request, "account.html", {"success": "Password updated successfully."})

    return redirect("account")


def get_logged_in_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return Signup.objects.filter(id=user_id).first()


# ==================== HOME ====================

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


# ==================== MOVIE DETAILS ====================

@user_login_required
def movie_detail(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    favorites = Favorite.objects.filter(
        user_id=request.session["user_id"]
    ).values_list("movie_id", flat=True)

    watch_later = WatchLater.objects.filter(
        user_id=request.session["user_id"]
    ).values_list("movie_id", flat=True)

    return render(request, "movie_detail.html", {
        "movie": movie,
        "favorites": favorites,
        "watch_later": watch_later,
    })


# ==================== PLAY MOVIE ====================

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
    ).exclude(id=movie.id)[:8]

    return render(request, "player.html", {
        "movie": movie,
        "favorites": favorites,
        "watch_later": watch_later,
        "related_movies": related_movies,
    })


# ==================== FAVORITES ====================

@user_login_required
def add_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    Favorite.objects.get_or_create(user_id=request.session["user_id"], movie=movie)
    return redirect(request.META.get("HTTP_REFERER", "index"))


@user_login_required
def remove_favorite(request, movie_id):
    Favorite.objects.filter(user_id=request.session["user_id"], movie_id=movie_id).delete()
    return redirect(request.META.get("HTTP_REFERER", "favorites"))


@user_login_required
def favorites(request):
    favorites = Favorite.objects.filter(user_id=request.session["user_id"]).select_related("movie")
    return render(request, "favorites.html", {"favorites": favorites})


# ==================== WATCH LATER ====================

@user_login_required
def add_watch_later(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    WatchLater.objects.get_or_create(user_id=request.session["user_id"], movie=movie)
    return redirect(request.META.get("HTTP_REFERER", "index"))


@user_login_required
def remove_watch_later(request, movie_id):
    WatchLater.objects.filter(user_id=request.session["user_id"], movie_id=movie_id).delete()
    return redirect(request.META.get("HTTP_REFERER", "watch_later"))


@user_login_required
def watch_later(request):
    movies = WatchLater.objects.filter(user_id=request.session["user_id"]).select_related("movie")
    return render(request, "watchlater.html", {"movies": movies})


@user_login_required
def watch_history(request):
    history = WatchHistory.objects.filter(user_id=request.session["user_id"]).select_related("movie")
    return render(request, "history.html", {"history": history})


# ==================== SEARCH ====================

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


# ==================== SINGLE MANAGE PANEL (GET) ====================

@admin_required
def manage_panel(request):

    context = {
        "total_movies": Movie.objects.count(),
        "total_users": Signup.objects.count(),
        "total_genres": Genre.objects.count(),
        "total_languages": Language.objects.count(),

        "movies": Movie.objects.select_related("genre", "language").order_by("-id"),
        "genres": Genre.objects.annotate(movie_count=Count("movies")).order_by("name"),
        "languages": Language.objects.annotate(movie_count=Count("movies")).order_by("name"),
        "users": Signup.objects.order_by("-id"),
    }
    return render(request, "manage.html", context)


# ==================== MOVIE ACTIONS (POST only, redirect back) ====================

def wants_json(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _validate_common_movie_fields(request):
    name = request.POST.get("name", "").strip()
    duration = request.POST.get("duration", "").strip()
    description = request.POST.get("description", "").strip()
    genre_id = request.POST.get("genre")
    language_id = request.POST.get("language")

    if not (name and duration and description and genre_id and language_id):
        return None, "All fields are required."

    if not Genre.objects.filter(id=genre_id).exists():
        return None, "Invalid genre selected."

    if not Language.objects.filter(id=language_id).exists():
        return None, "Invalid language selected."

    return {
        "name": name,
        "duration": duration,
        "description": description,
        "genre_id": genre_id,
        "language_id": language_id,
    }, None


@admin_required
def movie_add(request):
    if request.method == "POST":
        poster = request.FILES.get("poster")
        video = request.FILES.get("video")

        data, error = _validate_common_movie_fields(request)

        if data is None:
            if wants_json(request):
                return JsonResponse({"status": "error", "message": error}, status=400)
            messages.error(request, error)
            return redirect("manage_panel")

        if not poster or not video:
            error = "Poster and video are required."
            if wants_json(request):
                return JsonResponse({"status": "error", "message": error}, status=400)
            messages.error(request, error)
            return redirect("manage_panel")

        try:
            Movie.objects.create(
                name=data["name"],
                duration=data["duration"],
                description=data["description"],
                genre_id=data["genre_id"],
                language_id=data["language_id"],
                poster=poster,
                video=video,
            )
        except Exception:
            logger.exception("Failed to create movie")
            error = "Something went wrong while saving the movie."
            if wants_json(request):
                return JsonResponse({"status": "error", "message": error}, status=500)
            messages.error(request, error)
            return redirect("manage_panel")

        if wants_json(request):
            return JsonResponse({"status": "ok"})
        return redirect("manage_panel")

    return redirect("manage_panel")


@admin_required
def movie_edit(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == "POST":
        poster = request.FILES.get("poster")
        video = request.FILES.get("video")

        data, error = _validate_common_movie_fields(request)

        if data is None:
            if wants_json(request):
                return JsonResponse({"status": "error", "message": error}, status=400)
            messages.error(request, error)
            return redirect("manage_panel")

        movie.name = data["name"]
        movie.duration = data["duration"]
        movie.description = data["description"]
        movie.genre_id = data["genre_id"]
        movie.language_id = data["language_id"]

        if poster:
            movie.poster = poster

        if video:
            movie.video = video

        try:
            movie.save()
        except Exception:
            logger.exception("Failed to save movie %s", movie_id)
            error = "Something went wrong while saving the movie."
            if wants_json(request):
                return JsonResponse({"status": "error", "message": error}, status=500)
            messages.error(request, error)
            return redirect("manage_panel")

        if wants_json(request):
            return JsonResponse({"status": "ok"})
        return redirect("manage_panel")

    return redirect("manage_panel")


@admin_required
def movie_delete(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == "POST":
        movie.delete()
    return redirect("manage_panel")


# ==================== GENRE ACTIONS ====================

@admin_required
def genre_add(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name and not Genre.objects.filter(name=name).exists():
            Genre.objects.create(name=name)
    return redirect("manage_panel")


@admin_required
def genre_edit(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name and not Genre.objects.filter(name=name).exclude(id=genre.id).exists():
            genre.name = name
            genre.save()
    return redirect("manage_panel")


@admin_required
def genre_delete(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    if request.method == "POST":
        genre.delete()
    return redirect("manage_panel")


# ==================== LANGUAGE ACTIONS ====================

@admin_required
def language_add(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            Language.objects.create(name=name)
    return redirect("manage_panel")


@admin_required
def language_edit(request, language_id):
    language = get_object_or_404(Language, id=language_id)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            language.name = name
            language.save()
    return redirect("manage_panel")


@admin_required
def language_delete(request, language_id):
    language = get_object_or_404(Language, id=language_id)
    if request.method == "POST":
        language.delete()
    return redirect("manage_panel")


# ==================== USER ACTIONS ====================

@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(Signup, id=user_id)
    if request.method == "POST":
        user.delete()
    return redirect("manage_panel")