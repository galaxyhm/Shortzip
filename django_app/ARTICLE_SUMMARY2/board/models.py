from django.db import models
from accounts.models import MyUser
# Create your models here.


class NewsArticleInfo(models.Model):
    title = models.CharField(max_length=100)
    detail = models.TextField()
    url = models.CharField(unique=True, max_length=200)
    press = models.CharField(max_length=100)
    journalist = models.CharField(max_length=20)
    summary = models.CharField(max_length=1000)
    article_date = models.DateTimeField()
    modify_date = models.DateTimeField(blank=True, null=True)
    section = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'news_article_info'


class NewsArticleComments(models.Model):
    article_url = models.ForeignKey('NewsArticleInfo', models.DO_NOTHING, db_column='article_url')
    username = models.CharField(max_length=40)
    content = models.CharField(max_length=300, blank=True, null=True)
    sympathycount = models.IntegerField(db_column='sympathyCount')  # Field name made lowercase.
    antipathycount = models.IntegerField(db_column='antipathyCount')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'news_article_comments'


class UserSummarizationRequest(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.ForeignKey(MyUser, models.DO_NOTHING, db_column='userid')
    url = models.CharField(max_length=100)
    request_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_summarization_request'
