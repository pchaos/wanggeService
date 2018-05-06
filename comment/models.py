'评论应用模型'
from django.db import models
from django.contrib.auth.models import User
# 从别的app中导入文章模型
from stocks.models import ZXG

class BaseComment(models.Model):
    '基础评论模型'
    content = models.TextField('评论', max_length=500)
    time = models.DateTimeField('评论时间', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论者')
    class Meta:
        abstract = True

class ArticleComment(BaseComment):
    '文章评论'
    article = models.ForeignKey(ZXG, on_delete=models.CASCADE, verbose_name='评论')
    class Meta:
        ordering = ['-time']

class ArticleCommentReply(BaseComment):
    '文章评论回复(二级评论)'
    comment = models.ForeignKey(ArticleComment, on_delete=models.CASCADE, related_name='replies', verbose_name='一级评论')
    reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='回复对象')
    class Meta:
        ordering = ['time']