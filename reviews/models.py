from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Actor(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(help_text="Direct link to actor's square photo")

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    director = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    release_date = models.DateField()
    description = models.TextField()
    image = models.URLField()
    created = models.DateTimeField(default=timezone.now)
    trailer_url = models.URLField(blank=True, help_text="YouTube Embed link")
    movie_photos = models.TextField(blank=True, help_text="Paste Image URLs separated by commas")
    cast = models.ManyToManyField(Actor, related_name='movies', blank=True)
    users_wishlist = models.ManyToManyField(User, related_name='watchlist', blank=True)
    
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return self.title


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
    validators=[
        MinValueValidator(1),
        MaxValueValidator(10)
    ]
)
    comment = models.TextField(blank=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.user.username
