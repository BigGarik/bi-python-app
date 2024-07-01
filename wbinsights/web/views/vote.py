from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from web.models import Article


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
