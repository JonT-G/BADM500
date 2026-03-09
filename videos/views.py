"""
View functions for the BADM500 video-sharing platform.

Handles page rendering, authentication, video actions (like, subscribe,
save, comment-vote), notifications, and user profile management.
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, RegisterForm, VideoUploadForm
from .models import (
    Comment, CommentVote, Like, Notification, Profile, Subscription,
    Video, WatchHistory, WatchLater,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _notify(recipient, actor, verb, video=None):
    """Create a notification, skipping self-notifications and duplicates."""
    if recipient == actor:
        return
    Notification.objects.get_or_create(
        recipient=recipient, actor=actor, verb=verb, video=video,
    )

# ---------------------------------------------------------------------------
# Page views
# ---------------------------------------------------------------------------

def index(request):
    """Home page — public video grid with search and pagination."""
    query = request.GET.get('q', '').strip()
    qs = Video.objects.filter(visibility='public')
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(qs, 12)
    videos = paginator.get_page(request.GET.get('page'))
    return render(request, 'index.html', {'videos': videos, 'query': query})

def watch(request, pk):
    """Video watch page — player, comments, related videos."""
    video = get_object_or_404(Video, pk=pk)
    video.views += 1
    video.save(update_fields=['views'])

    user = request.user
    user_liked = user_disliked = is_subscribed = is_saved = False

    if user.is_authenticated:
        WatchHistory.objects.update_or_create(user=user, video=video)

        like_obj = Like.objects.filter(video=video, user=user).first()
        if like_obj:
            user_liked = like_obj.is_like
            user_disliked = not like_obj.is_like

        is_subscribed = Subscription.objects.filter(
            subscriber=user, channel=video.author,
        ).exists()
        is_saved = WatchLater.objects.filter(user=user, video=video).exists()

    # Handle new comment
    if request.method == 'POST' and 'comment_text' in request.POST and user.is_authenticated:
        text = request.POST.get('comment_text', '').strip()
        if text:
            Comment.objects.create(video=video, author=user, text=text)
            _notify(video.author, user, 'commented', video)
            messages.success(request, 'Comment posted!')
            return redirect('watch', pk=pk)

    comments = video.comments.all()
    related_videos = Video.objects.filter(visibility='public').exclude(pk=pk)[:5]

    # Annotate each comment with the current user's vote
    if user.is_authenticated:
        user_votes = dict(
            CommentVote.objects.filter(user=user, comment__in=comments)
            .values_list('comment_id', 'is_upvote')
        )
        for c in comments:
            c.user_upvoted = user_votes.get(c.pk) is True
            c.user_downvoted = user_votes.get(c.pk) is False
    else:
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
    """Upload a new video."""
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.save()
            messages.success(request, 'Video uploaded successfully!')
            return redirect('watch', pk=video.pk)
    else:
        form = VideoUploadForm()
    return render(request, 'upload.html', {'form': form})

def profile(request, username):
    """User profile page — videos grid and about tab."""
    user = get_object_or_404(User, username=username)
    videos = Video.objects.filter(author=user, visibility='public')
    profile_obj, _ = Profile.objects.get_or_create(user=user)

    is_subscribed = False
    if request.user.is_authenticated and request.user != user:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user, channel=user,
        ).exists()

    return render(request, 'profile.html', {
        'profile_user': user,
        'profile': profile_obj,
        'videos': videos,
        'sub_count': user.subscribers.count(),
        'total_views': sum(v.views for v in user.videos.all()),
        'is_subscribed': is_subscribed,
        'tab': request.GET.get('tab', 'videos'),
    })


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------
def register_view(request):
    """Create a new user account."""
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created! Welcome to BADM500.')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Log in an existing user."""
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', ''),
            password=request.POST.get('password', ''),
        )
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    """Log out the current user."""
    logout(request)
    return redirect('index')

# ---------------------------------------------------------------------------
# Action views
# ---------------------------------------------------------------------------
@login_required
def toggle_like(request, pk):
    """Like or dislike a video (toggle).

    Query param ``type`` controls the action: ``like`` (default) or ``dislike``.
    """
    video = get_object_or_404(Video, pk=pk)
    is_like = request.GET.get('type', 'like') == 'like'

    like_obj, created = Like.objects.get_or_create(
        video=video, user=request.user, defaults={'is_like': is_like},
    )
    if not created:
        if like_obj.is_like == is_like:
            like_obj.delete()          # toggle off
        else:
            like_obj.is_like = is_like  # switch like ↔ dislike
            like_obj.save()

    # Notify video author on like (not dislike)
    if Like.objects.filter(video=video, user=request.user, is_like=True).exists():
        _notify(video.author, request.user, 'liked', video)

    return redirect('watch', pk=pk)

@login_required
def subscribe(request, username):
    """Toggle subscription to a channel."""
    channel = get_object_or_404(User, username=username)
    if request.user == channel:
        return redirect('profile', username=username)

    sub, created = Subscription.objects.get_or_create(
        subscriber=request.user, channel=channel,
    )
    if not created:
        sub.delete()
    else:
        _notify(channel, request.user, 'subscribed')

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def toggle_watch_later(request, pk):
    """Add / remove a video from watch-later."""
    video = get_object_or_404(Video, pk=pk)
    obj, created = WatchLater.objects.get_or_create(user=request.user, video=video)
    if not created:
        obj.delete()

    return redirect('watch', pk=pk)

@login_required
def vote_comment(request, pk):
    """Toggle upvote / downvote on a comment."""
    comment = get_object_or_404(Comment, pk=pk)
    is_upvote = request.GET.get('type', 'up') == 'up'

    vote_obj, created = CommentVote.objects.get_or_create(
        comment=comment, user=request.user,
        defaults={'is_upvote': is_upvote},
    )
    if not created:
        if vote_obj.is_upvote == is_upvote:
            vote_obj.delete()
        else:
            vote_obj.is_upvote = is_upvote
            vote_obj.save()

    # Notify comment author on upvote
    if CommentVote.objects.filter(comment=comment, user=request.user, is_upvote=True).exists():
        _notify(comment.author, request.user, 'upvoted', comment.video)

    return redirect('watch', pk=comment.video.pk)


# ---------------------------------------------------------------------------
# Library / list views
# ---------------------------------------------------------------------------
@login_required
def history(request):
    """Watch history — most recently watched first."""
    entries = WatchHistory.objects.filter(user=request.user).select_related('video', 'video__author')
    return render(request, 'history.html', {'videos': [e.video for e in entries]})

@login_required
def watch_later_list(request):
    """Saved-for-later videos."""
    entries = WatchLater.objects.filter(user=request.user).select_related('video', 'video__author')
    return render(request, 'watch_later.html', {'videos': [e.video for e in entries]})

@login_required
def liked_videos(request):
    """Videos the current user has liked."""
    likes = Like.objects.filter(user=request.user, is_like=True).select_related('video', 'video__author')
    return render(request, 'liked_videos.html', {'videos': [l.video for l in likes]})


# ---------------------------------------------------------------------------
# Profile & video management
# ---------------------------------------------------------------------------
@login_required
def edit_profile(request):
    """Edit the logged-in user's bio and avatar."""
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile_obj)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def delete_video(request, pk):
    """Delete a video (owner only). Requires POST confirmation."""
    video = get_object_or_404(Video, pk=pk, author=request.user)
    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Video deleted.')
        return redirect('profile', username=request.user.username)
    return render(request, 'confirm_delete.html', {'video': video})

# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
@login_required
def notifications_list(request):
    """Show all notifications — marks unread ones as read on view."""
    notifs = list(
        request.user.notifications.select_related('actor', 'video').all()[:50]
    )
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifs})
