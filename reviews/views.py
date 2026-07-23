from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Actor
from .forms import ReviewForm
from .forms import ReviewForm
from django.db.models import Avg, Count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from datetime import date

def movie_list(request):
    trending_movies = Movie.objects.annotate(
        total_reviews=Count('review')
    ).order_by('-total_reviews')[:12]

    return render(
        request,
        'reviews/movie_list.html',
        {
            'trending_movies': trending_movies
        }
    )


@login_required
def explore(request):
    query = request.GET.get('q')
    genre_filter = request.GET.get('genre')
    
    today = date(2026, 5, 9)
    three_months_ago = date(2026, 2, 9) 

    movies = Movie.objects.annotate(
        avg_rating=Avg('review__rating'),
        review_count=Count('review')
    )

    fans_favorites = movies.filter(avg_rating__gte=8.0).order_by('-avg_rating')[:6]

    latest_releases = Movie.objects.filter(
        release_date__range=[three_months_ago, today]
    ).order_by('-release_date')[:6]

    upcoming_movies = Movie.objects.filter(
        release_date__gt=today
    ).order_by('release_date')[:6]

    if query:
        movies = movies.filter(title__icontains=query)
    if genre_filter:
        movies = movies.filter(genre__iexact=genre_filter)

    popular_actors = Actor.objects.all()[:14]

    genres = sorted(set(Movie.objects.values_list('genre', flat=True)))

    return render(
        request,
        'reviews/explore.html',
        {
            'movies': movies,
            'query': query,
            'genres': genres,
            'fans_favorites': fans_favorites,
            'latest_releases': latest_releases,
            'upcoming_movies': upcoming_movies,
            'popular_actors': popular_actors,
            'selected_genre': genre_filter,
        }
    )


@login_required
def section_list(request, section_type):
    today = date(2026, 5, 9)
    three_months_ago = date(2026, 2, 9)
    
    # Base QuerySet
    movies = Movie.objects.annotate(avg_rating=Avg('review__rating'))
    

    if section_type == 'favorites':
        title = "Fans' Favorites"
        movies = movies.filter(avg_rating__gte=8.0).order_by('-avg_rating')
    elif section_type == 'latest':
        title = "Latest Releases"
        movies = movies.filter(release_date__range=[three_months_ago, today]).order_by('-release_date')
    elif section_type == 'upcoming':
        title = "Coming Soon"
        movies = movies.filter(release_date__gt=today).order_by('release_date')
    elif section_type == 'all':
        title = "All Movies"
        movies = movies.order_by('-release_date') 
    else:
        return redirect('explore')

    return render(request, 'reviews/section_list.html', {
        'movies': movies,
        'title': title

    })




@login_required
def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)

    today = date(2026, 5, 9) 

    photos_list = [url.strip() for url in movie.movie_photos.split(',')] if movie.movie_photos else []

    cast_list = movie.cast.all() 

    more_like_this = Movie.objects.filter(genre=movie.genre).exclude(id=movie.id)[:6]
    
    reviews = movie.review_set.all()
    
    review_count = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user 
            review.save()
            return redirect('movie_detail', slug=movie.slug)
    else:
        form = ReviewForm()

    return render(
        request, 
        'reviews/movie_detail.html', 
        {
            'movie': movie,
            'today': today,
            'photos_list': photos_list,
            'cast_list': cast_list,
            'more_like_this': more_like_this,
            'reviews': reviews,
            'form': form,
            'avg_rating': avg_rating,
            'review_count': review_count
        }
    )



@login_required
def toggle_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if movie.users_wishlist.filter(id=request.user.id).exists():
        movie.users_wishlist.remove(request.user)
    else:
        movie.users_wishlist.add(request.user)
    return redirect('movie_detail', slug=movie.slug)


@login_required
def watchlist(request):
    # Get only the movies the current user has saved
    my_movies = request.user.watchlist.all()
    return render(request, 'reviews/watchlist.html', {'movies': my_movies})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}! You can now login.')
            return redirect('login') 
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def logout_confirm(request):
    return render(request, 'registration/logout_confirm.html')

@login_required
def profile(request):
    user_reviews = request.user.reviews.all()
    watchlist_count = request.user.watchlist.count()
    
    return render(request, 'registration/profile.html', {
        'user_reviews': user_reviews,
        'watchlist_count': watchlist_count,
    })

@login_required
def all_actors(request):    
    actors = Actor.objects.all().order_by('name')
    return render(request, 'reviews/all_actors.html', {'actors': actors})
