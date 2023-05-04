from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.index, name='index'),
    path('crawl/', views.text_summarizae_request_ajax, name='text_summarizae_request_ajax'),
    path('summarize/', views.news_summarizae_request_ajax, name='news_summarizae_request_ajax'),
    path('comments/', views.news_comments_request_ajax, name='news_comments_request_ajax'),

    
    # path('summarize/', views.summarize, name='summarize'),
]
