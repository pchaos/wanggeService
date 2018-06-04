# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : hsgtcgholdview.py

Description :

@Author :       pchaos

date：          18-6-1
-------------------------------------------------
Change Activity:
               18-6-1:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
from django.views import generic
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from stocks.models import HSGTCG
from stocks.models import HSGTCGHold
from stocks.serializers import HSGTCGHoldSerializer


@api_view(['GET', 'POST'])
def HSGTCGHoldView(request, format=None):
    """
    List all snippets, or create a new snippet.
    """
    if request.method == 'GET':
        values = HSGTCGHold.objects.all()
        serializer = HSGTCGHoldSerializer(values, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = HSGTCGHoldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)