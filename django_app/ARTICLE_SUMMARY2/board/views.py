from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views.decorators.http import (require_http_methods,
                                            require_safe, require_POST)

from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import JsonResponse
import json
from .newsCrawler import NewsCrawler
import requests
import re
from . import models
from django.db.models import Q

import pandas as pd
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
def news_summarizae_request_ajax(request):
    # print(request.body)
    url = json.loads(request.body)['url']
    url = url.replace('/mnews','')
    url = url.replace('/newspaper','')

    naver_url_regex = r'(http|https)://n.news.naver.com/article/\d+/\d+'
    regex = re.compile(naver_url_regex)
    url = regex.match(url)
    print(url)
    
    if not url :
        print('error 올바르지 않는 url')
        # return 해서 어떻게 처리하셈 
    url = url[0]

    # DB에서 해당 url에 맞는 데이터 필드 가져옴.
    crawl_data_dict = NewsCrawler.navercrawl(url)
    news_article = models.NewsArticleInfo()
    request_body = {
        "text" : crawl_data_dict['text'].strip()

    }
    # print('test1 통과')
    # DB에 해당 URL로 있는것을 조회 
    # 입력받은 URL을 가진 기사가 데이터베이스에 존재하는지 확인.
    if models.NewsArticleInfo.objects.filter(url=url) :
        # 해당 URL을 가진 기사가 데이터베이스에 존재하면, 수정일자를 비교하여 최신 버전인지 확인.
        if models.NewsArticleInfo.objects.filter(Q(url=url) & Q(modify_date__isnull=True)) or  models.NewsArticleInfo.objects.filter(Q(url=url) & Q(modify_date = crawl_data_dict.get('modify_date'))):
            news_article = models.NewsArticleInfo.objects.get(url=url)

            return JsonResponse(
                {
                    'summarize' : news_article.summary,
                    'title' : crawl_data_dict['title'],
                    'newspaper' : crawl_data_dict['press'],
                    'category' : crawl_data_dict['section'],
                }
            )
        # 최신 버전이 아닐 경우, 기사의 내용을 업데이트하고 요약을 다시 생성.
        else :
            news_article = models.NewsArticleInfo.objects.get(url=url)
            news_article.detail = crawl_data_dict['text']
            news_article.modify_date = crawl_data_dict['modify_date']
            request_body = {
                "text" : crawl_data_dict['text']

            }
            request_body = json.dumps(request_body)
            r = requests.post('http://13.208.62.74:8908/summarize/text/', data=request_body)

            #정상적인 응답을 못 받았을때
            if r.status_code != 200 :
                pass
            json_data = r.json()['message'][0].get('summary_text').strip()
            news_article.summary = json_data
            news_article.update()
            return JsonResponse(
                {
                    'summarize' : json_data,
                    'title' : crawl_data_dict['title'],
                    'newspaper' : crawl_data_dict['press'],
                    'category' : crawl_data_dict['section'],
                
                }
            )



    # DB 모델 객체의 값 채움
    news_article.title = crawl_data_dict['title']
    news_article.detail = crawl_data_dict['text']
    news_article.url = url
    news_article.press = crawl_data_dict['press']
    news_article.journalist = crawl_data_dict['reporter']
    news_article.section = crawl_data_dict['section']
    news_article.article_date = crawl_data_dict['write_date']
    if crawl_data_dict['modify_date'] != -1:
        news_article.modify_date = crawl_data_dict['modify_date']
    else :
        pass
    request_body = json.dumps(request_body)
    print(len(crawl_data_dict['text']))
    request_summarize = requests.post('http://13.208.62.74:8908/summarize/text/', data=request_body)
    if request_summarize.status_code != 200 :
        pass
    json_data = request_summarize.json()['message'][0].get('summary_text').strip()
    news_article.summary = json_data
    # 모델저장 
    news_article.save()

    print(json_data)
    return JsonResponse(
        {
            'title' : crawl_data_dict['title'],
            'newspaper' : crawl_data_dict['press'],
            'category' : crawl_data_dict['section'],
            'summarize' : json_data,           
        }
    )
    

@require_http_methods(['POST'])
def news_comments_request_ajax(request):

    url = json.loads(request.body)['url']
    url = url.replace('/mnews','')
    url = url.replace('/newspaper','')
    naver_url_regex = r'(http|https)://n.news.naver.com/article/\d+/\d+'
    regex = re.compile(naver_url_regex)
    url = regex.match(url)
    print(f'\n 최종 url : {url}\n')
    
    if not url :
        print('error 올바르지 않는 url')
    url = url[0]

    comments_object = models.NewsArticleComments()
    crawl_comment_list = NewsCrawler.get_news_comment(url=url)
    # crawl_comment_dict = dict()
    # crawl_comment_dict['comments_data'] = crawl_comment_list
    

    for comment in crawl_comment_list:
        comments_object.username = comment['userName']
        comments_object.contents = comment['contents']
        comments_object.sympathyCount = comment['sympathyCount']
        comments_object.antipathyCount = comment['antipathyCount']
        comments_object.save()

    
    # DB 모델 객체의 값 채움

    return JsonResponse(
        {
            'comments' : crawl_comment_list
        }
    )



@require_http_methods(['POST'])
def text_summarizae_request_ajax(request):


    cond = {
        "url" : "https://n.news.naver.com/article/018/0005472525"

    }
    jsonData = json.dumps(cond)
    # r = requests.post('http://localhost:10000/crawl/naver/', data=jsonData)
    print(r.status_code)
    # print(r.json())
    # data = json.loads(m.body)
    context = {
        'result' : 'error '
    }
    # if data['url'] :
    return JsonResponse(r.json())
     
    
def ajax_test(request) :
        
    context = {'test' :'test'}

    return JsonResponse(context)





