"""
Render the main pages of the site.
Each function receives a request, fetches data from the database, and returns an HTML page.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import VideoUploadForm
from ..models import Comment, CommentVote, Like, Profile, Subscription, Video, WatchHistory, WatchLater
from .actions import _notify


def index(request):
    """
    Home page, shows all public videos, newest first.
    """
    query = request.GET.get('q', '').strip()

    # Start with all public videos
    videos = Video.objects.filter(visibility='public')

    if query:
        # Djangos way of doing OR operations.
        videos = videos.filter(
            Q(title__icontains=query) | Q(description__icontains=query) # icontains is case-insensitive, so "music" matches "Music" or "MUSIC".
        )

    # Paginator splits the full list of videos into pages of 12.
    paginator = Paginator(videos, 12)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'index.html', {'videos': page, 'query': query})


def watch(request, pk):
    """
    Watch page, shows the video player, like/save/subscribe buttons, and comments.
    Also handle new comment submissions.
    """
    video = get_object_or_404(Video, pk=pk)
    video.views += 1
    video.save(update_fields=['views']) #update_fields means only that one column is saved, not the entire row, faster and avoids accidental overwrites.

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
            return redirect('watch', pk=pk)  # redirect to avoid resubmitting on refresh

    comments = video.comments.all()
    related_videos = Video.objects.filter(visibility='public').exclude(pk=pk)[:5]

    # checks for if user has downvoted or liked comments on a video
    if user.is_authenticated:
        user_votes = dict(
            CommentVote.objects.filter(user=user, comment__in=comments)
            .values_list('comment_id', 'is_upvote')
        )
        for c in comments:
            # returns None if the user interacted on this comment
            c.user_upvoted   = user_votes.get(c.pk) is True
            c.user_downvoted = user_votes.get(c.pk) is False
    else:
        # Not logged in, no reactions to comment possible
        for c in comments:
            c.user_upvoted = c.user_downvoted = False

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
    Redirect to /login/ if user is not logged in.
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

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'profile': profile_obj,
        'videos': videos,
        'sub_count': profile_user.subscribers.count(),
        'total_views': sum(v.views for v in profile_user.videos.all()),
        'is_subscribed': is_subscribed,
        'tab': request.GET.get('tab', 'videos'),  
    })
