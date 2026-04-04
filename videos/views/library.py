"""
Profile and account management.
Includes watch history, watch later, liked videos, notifications,
and profile/video editing. All require user to be logged in.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import ProfileForm
from ..models import Like, Profile, Video, WatchHistory, WatchLater

@login_required
def history(request):
    """Shows all videos the user has watched, most recent first."""
    entries = WatchHistory.objects.filter(user=request.user).select_related('video', 'video__author')
    return render(request, 'history.html', {'videos': [e.video for e in entries]})

@login_required
def watch_later_list(request):
    """Shows all videos the user has saved to watch later."""
    entries = WatchLater.objects.filter(user=request.user).select_related('video', 'video__author')
    return render(request, 'watch_later.html', {'videos': [e.video for e in entries]})

@login_required
def liked_videos(request):
    """Shows all videos the user has liked (thumbs up only, not dislikes)."""
    likes = Like.objects.filter(user=request.user, is_like=True).select_related('video', 'video__author')
    return render(request, 'liked_videos.html', {'videos': [like.video for like in likes]})

@login_required
def notifications_list(request):
    """
    Shows the 100 most recent notifications for the user.
    """
    notifs = list(
        request.user.notifications.select_related('actor', 'video').all()[:100]
    )
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifs})


@login_required
def edit_profile(request):
    """
    Profile edit page, lets the user update their bio and avatar.
    """
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
    """
    Delete a video, only the author can do this.
    """
    video = get_object_or_404(Video, pk=pk, author=request.user)

    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Video deleted.')
        return redirect('profile', username=request.user.username)

    return render(request, 'confirm_delete.html', {'video': video})
