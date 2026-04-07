"""
Render the main pages of the site.
Each function receives a request, fetches data from the database, and returns an HTML page.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import VideoUploadForm
from ..models import Comment, CommentVote, Like, Profile, Subscription, Video, WatchHistory, WatchLater
from .actions import _notify

def index(request):
    """
    Home page, shows all public videos, newest first.
    """
    query = request.GET.get('q', '').strip()

    videos = Video.objects.filter(visibility='public')

    if query:
        # Djangos way of doing OR and AND operations.
        videos = videos.filter(
            Q(title__icontains=query) | Q(description__icontains=query) # icontains is case-insensitive, so "music" matches "Music" or "MUSIC".
        )

    # Paginator splits the full list of videos into pages of 12.
    paginator = Paginator(videos, 12)
    page = paginator.get_page(request.GET.get('page'))
    page_base = f"?q={query}&" if query else "?"

    return render(request, 'index.html', {'videos': page, 'query': query, 'page_base': page_base})


def watch(request, pk):
    """
    Watch page, shows the video player, like/save/subscribe buttons, and comments.
    Also handle new comment submissions.
    """
    video = get_object_or_404(Video, pk=pk)
    video.views += 1
    video.save(update_fields=['views']) 
    user = request.user

    # Default state for all buttons, updated if user is logged in
    user_liked = user_disliked = is_subscribed = is_saved = False

    if user.is_authenticated:
        # Keep track if user watched this video (or update the timestamp if they watched before)
        WatchHistory.objects.update_or_create(user=user, video=video)

        # Check if the user has liked or disliked this video
        like_obj = Like.objects.filter(video=video, user=user).first()
        if like_obj:
            user_liked = like_obj.is_like
            user_disliked = not like_obj.is_like

        is_subscribed = Subscription.objects.filter(subscriber=user, channel=video.author).exists()
        is_saved = WatchLater.objects.filter(user=user, video=video).exists()

    # Handling of new comment being posted
    if request.method == 'POST' and 'comment_text' in request.POST and user.is_authenticated:
        text = request.POST.get('comment_text', '').strip()
        if text:
            Comment.objects.create(video=video, author=user, text=text)
            _notify(video.author, user, 'commented', video)
            messages.success(request, 'Comment posted!')
            return redirect('watch', pk=pk) 

    comments = video.comments.all()
    related_videos = Video.objects.filter(visibility='public').exclude(pk=pk)[:5]

    # track which comments user has voted on
    user_votes = {}
    if user.is_authenticated:
        user_votes = dict(
            CommentVote.objects.filter(user=user, comment__in=comments)
            .values_list('comment_id', 'is_upvote')
        )
    for c in comments:
        c.user_upvoted   = user_votes.get(c.pk) is True
        c.user_downvoted = user_votes.get(c.pk) is False
    #render watch page fecthing data from the database and pass it to the template 
    return render(request, 'watch.html', {
        'video': video,
        'comments': comments,
        'related_videos': related_videos,
        'user_liked': user_liked,
        'user_disliked': user_disliked,
        'is_subscribed': is_subscribed,
        'is_saved': is_saved,
    })


@login_required
def upload(request):
    """
    Upload page, shows the upload form and saves the video.
    """
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False) # do not save to database yet, so author can be set.
            video.author = request.user
            video.save()
            messages.success(request, 'Video uploaded successfully!')
            return redirect('watch', pk=video.pk)
    else:
        form = VideoUploadForm()
    # Redirect to /login/ if user is not logged in.
    return render(request, 'upload.html', {'form': form})


def profile(request, username):
    """
    Profile page, shows a users info, stats and public videos.
    """
    profile_user = get_object_or_404(User, username=username)
    videos = Video.objects.filter(author=profile_user, visibility='public')
    profile_obj, _ = Profile.objects.get_or_create(user=profile_user)

    # Check if the logged-in user is subscribed to this channel
    is_subscribed = False
    if request.user.is_authenticated and request.user != profile_user:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user, channel=profile_user,
        ).exists()

    display_name = profile_user.get_full_name() or profile_user.username

    #render profile fecting data from database and passing it to the template
    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'profile': profile_obj,
        'videos': videos,
        'sub_count': profile_user.subscribers.count(),
        'total_views': profile_user.videos.aggregate(total=Sum('views'))['total'] or 0,
        'is_subscribed': is_subscribed,
        'tab': request.GET.get('tab', 'videos'),
        'display_name': display_name,
    })
