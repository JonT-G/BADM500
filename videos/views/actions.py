"""
Handle user interactions that write to the database.
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import Comment, CommentVote, Like, Notification, Subscription, Video, WatchLater

def _notify(recipient, actor, verb, video=None):
    """
    Create a notification — but skip it if the user is acting on their own content.
    """
    if recipient == actor:
        return  
    # no self-notifications, like liking your own video
    Notification.objects.get_or_create( recipient=recipient, actor=actor, verb=verb, video=video,)


@login_required
def toggle_like(request, pk):
    """
    Like or dislike a video. Reads type=like or type=dislike from the URL.
    Returns JSON to not refresh page.
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
            #leftside is_like is database field and rightside is the new value from the URL
            like_obj.is_like = is_like  # clicked the other button and overwrite it
            like_obj.save()

    # Only notify on a like, not a dislike
    if Like.objects.filter(video=video, user=request.user, is_like=True).exists():
        _notify(video.author, request.user, 'liked', video)

    user_like = Like.objects.filter(video=video, user=request.user).first()
    return JsonResponse({
        'liked':         user_like is not None and user_like.is_like,
        'disliked':      user_like is not None and not user_like.is_like,
        'like_count':    video.like_count,
        'dislike_count': video.dislike_count,
    })


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
        return JsonResponse({'error': 'Cannot subscribe to yourself.'}, status=400)

    sub, created = Subscription.objects.get_or_create(
        subscriber=request.user, channel=channel,
    )
    if not created:
        sub.delete()  # already subscribed, unsubscribe instead
        is_subscribed = False
    else:
        _notify(channel, request.user, 'subscribed')
        is_subscribed = True

    #Json to not refresh page when action is performed
    return JsonResponse({
        'subscribed': is_subscribed,
        'sub_count':  channel.subscribers.count(),
    })


@login_required
def toggle_watch_later(request, pk):
    """Add a video to Watch Later, or remove it if already saved."""
    video = get_object_or_404(Video, pk=pk)
    obj, created = WatchLater.objects.get_or_create(user=request.user, video=video)
    if not created:
        obj.delete()
        is_saved = False
    else:
        is_saved = True
    return JsonResponse({'saved': is_saved})


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
            vote_obj.delete()           
        else:
            vote_obj.is_upvote = is_upvote
            vote_obj.save()

    if CommentVote.objects.filter(comment=comment, user=request.user, is_upvote=True).exists():
        _notify(comment.author, request.user, 'upvoted', comment.video)

    user_vote = CommentVote.objects.filter(comment=comment, user=request.user).first()
    return JsonResponse({
        'upvoted':        user_vote is not None and user_vote.is_upvote,
        'downvoted':      user_vote is not None and not user_vote.is_upvote,
        'upvote_count':   comment.upvote_count,
        'downvote_count': comment.downvote_count,
    })
