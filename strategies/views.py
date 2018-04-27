from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template import loader
from django.views import generic
from .models import StrategyType, Strategy, StrategyDetail
# from django.http import HttpResponse
# from polls.models import Question

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     output = ', '.join([q.question_text for q in latest_question_list])
#     return HttpResponse(output)

class IndexView(generic.ListView):
    template_name = 'strategies/index.html'
    context_object_name = 'strategy_list'  # 对应index.html中的{% for question in latest_question_list %}

    def get_queryset(self):
        """返回"""
        return Strategy.objects.order_by('code')

def detail(request, strategy_id):
    pass
