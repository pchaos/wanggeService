from django.shortcuts import render
from django.views.generic.list import ListView
from .models import ArticleComment, ArticleCommentReply
from .forms import ArticleCommentForm

class ArticleCommentView(ListView):
    '文章评论列表'
    model = ArticleComment
    # 前端使用Ajax请求评论数据，故该模板仅包含评论部分
    template_name = 'comment/article_comment.html'
    context_object_name = 'comment_list'
    # 分页，每页10条评论
    paginate_by = 10

    # 筛选目标文章的评论，id为url中的参数
    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if context["page_obj"].number == 1 and self.request.user.is_authenticated:
            # 评论的第一页需要提供表单让用户创建新评论
            context['form'] = ArticleCommentForm({'article': self.kwargs['id']})
        elif context["page_obj"].number == 1:
            # 没有登录的用户需要登录，传id是为了在评论中创建url，详细的在模板中解释
            context['id'] = self.kwargs['id']

        # 计算评论的次序
        first_num = context["paginator"].count - \
            self.paginate_by * (context["page_obj"].number - 1)
        last_num = first_num - self.paginate_by
        context['comment_list'] = zip(range(first_num, last_num, -1), context['comment_list'])
        return context
