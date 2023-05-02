from django.db import models

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