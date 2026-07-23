from django.contrib import admin
from .models import Movie, Review, Actor

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'director', 'genre', 'release_date']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'created']
    list_filter = ['created', 'rating']
    search_fields = ['user__username', 'comment']
