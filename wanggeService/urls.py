"""wanggeService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from django.views.generic.base import RedirectView
# from stocks import views
from stocks.views import UserViewSet, GroupViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

# router.register(r'api/stocks/stocks', views.stockcode_list)
# router.register(r'stockcodedetail', views.stockcode_detail)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    # url(r'^', include('strategies.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('stocks.urls', namespace='stocks')),
    url(r'^api/comment/', include('comment.urls', namespace='comments')),
    url(r'^polls/', include('polls.urls')),
    url(r'^strategies/', include('strategies.urls')),

]
