from django.contrib import admin
from . models import *

admin.site.register(Signup)
admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Movie)
admin.site.register(Favorite)
admin.site.register(WatchHistory)

