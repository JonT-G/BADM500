"""
Handle user interactions that write to the database.
None of these render a page, so they all just redirect back after doing their work.
All require the user to be logged in (@login_required).
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from ..models import Comment, CommentVote, Like, Notification, Subscription, Video, WatchLater

def _notify(recipient, actor, verb, video=None):
    """
    Create a notification — but skip it if the user is acting on their own content.
    """
    if recipient == actor:
        return  
    Notification.objects.get_or_create( # no self-notifications (e.g. liking your own video)
        recipient=recipient, actor=actor, verb=verb, video=video,
    )


@login_required
def toggle_like(request, pk):
    """
    Like or dislike a video. Reads type=like or type=dislike from the URL.
    """
    video = get_object_or_404(Video, pk=pk)
    is_like = request.GET.get('type', 'like') == 'like'

    like_obj, created = Like.objects.get_or_create(
        video=video, user=request.user,
        defaults={'is_like': is_like},  # only used when creating a new row
    )

    if not created:
        if like_obj.is_like == is_like:
            like_obj.delete()           # click again and it removes the like/dislike
        else:
            like_obj.is_like = is_like  # click the opposite and it switches from like to dislike or vice versa
            like_obj.save()

    # Only notify on a like, not a dislike
    if Like.objects.filter(video=video, user=request.user, is_like=True).exists():
        _notify(video.author, request.user, 'liked', video)
    return redirect('watch', pk=pk)


@login_required
def subscribe(request, username):
    """
    Manage subscription to a channel.
    If not subscribed then subscribe and notify the channel user.
    If already subscribed then unsubscribe.
    """
    channel = get_object_or_404(User, username=username)

    # Cant subscribe to yourself.
    if request.user == channel:
        return redirect('profile', username=username)

    sub, created = Subscription.objects.get_or_create(
        subscriber=request.user, channel=channel,
    )
    if not created:
        sub.delete()  # already subscribed, unsubscribe instead
    else:
        _notify(channel, request.user, 'subscribed')

    # Go back to whatever page the user came from (profile or watch page)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def toggle_watch_later(request, pk):
    """Add a video to Watch Later, or remove it if already saved."""
    video = get_object_or_404(Video, pk=pk)
    obj, created = WatchLater.objects.get_or_create(user=request.user, video=video)
    if not created:
        obj.delete()
    return redirect('watch', pk=pk)


@login_required
def vote_comment(request, pk):
    """
    Upvote or downvote a comment. Reads type=up or type=down from the URL.
    """
    comment = get_object_or_404(Comment, pk=pk)
    is_upvote = request.GET.get('type', 'up') == 'up'

    vote_obj, created = CommentVote.objects.get_or_create(
        comment=comment, user=request.user,
        defaults={'is_upvote': is_upvote},
    )

    if not created:
        if vote_obj.is_upvote == is_upvote:
            vote_obj.delete()           # click again and it removes the upvote/downvote
        else:
            vote_obj.is_upvote = is_upvote  # click the opposite and it switches from upvote to downvote or vice versa
            vote_obj.save()

    # Only notify on upvote, not downvote
    if CommentVote.objects.filter(comment=comment, user=request.user, is_upvote=True).exists():
        _notify(comment.author, request.user, 'upvoted', comment.video)

    return redirect('watch', pk=comment.video.pk)
