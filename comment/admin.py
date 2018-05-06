from django.contrib import admin
from .models import ArticleComment
from .models import ArticleCommentReply

# Register your models here.

admin.site.register(ArticleComment)
admin.site.register(ArticleCommentReply)
