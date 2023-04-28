from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views.decorators.http import (require_http_methods,
                                            require_safe, require_POST)

from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import JsonResponse
import json
from .newsCrawler import NewsCrawler

# Create your views here.

@require_safe
def index(request):
    return render(request, 'board/index.html')


# @login_required
# @require_http_methods(['GET', 'POST'])
# def create(request):
#     if request.method == 'POST':
#         form = UserForm()
#         if form.is_valid():
#             article = form.save(commit=False)
#             article.username = request.username
#             article.save()
#             return redirect('board:detail', article.pk)
#     else:
#         form = UserForm()
#         context = {'form' : form}
#         return render(request, 'board/join_membership.html', context)


# def summarize(request):
#     return render()



@require_http_methods(['POST'])
def text_summarizae_request_ajax(request):

    data = json.loads(request.body)
    context = {
        'result' : 'error '
    }
    if data['url'] :
        return JsonResponse(context)
     
    

    

    return JsonResponse(context)





