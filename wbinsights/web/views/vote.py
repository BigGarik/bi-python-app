from django.apps import apps
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from vote.models import VoteModel

from web.models import Article


def get_model_by_name(model_name):
    try:
        return apps.get_model(model_name)
    except LookupError:
        raise Http404(f"Model {model_name} not found")


@login_required
def upvote(request, pk):
    article = Article.objects.get(pk=pk)
    user = request.user
    if article.votes.exists(user.id):
        article.votes.delete(user.id)
    else:
        article.votes.up(user.id)
    return JsonResponse({'status': 'ok'})

@login_required
def downvote(request, pk):
    obj = Article.objects.get(pk=pk)
    user = request.user
    obj.votes.down(user.id)
    return JsonResponse({'status': 'ok'})


@login_required
def universal_vote(request, model_name, pk):
    Model = get_model_by_name(model_name)

    if not issubclass(Model, VoteModel):
        return JsonResponse({'status': 'error', 'message': 'Model does not support voting'}, status=400)

    obj = get_object_or_404(Model, pk=pk)
    user = request.user

    action = request.POST.get('action', 'up')

    if action == 'up':
        if obj.votes.exists(user.id):
            obj.votes.delete(user.id)
            status = 'unliked'
        else:
            obj.votes.up(user.id)
            status = 'liked'
    elif action == 'down':
        if obj.votes.exists(user.id):
            obj.votes.delete(user.id)
            status = 'unvoted'
        else:
            obj.votes.down(user.id)
            status = 'downvoted'
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    return JsonResponse({
        'status': 'ok',
        'action': status,
        'count': obj.votes.count()
    })