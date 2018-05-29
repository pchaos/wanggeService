from django.shortcuts import render

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from stocks.serializers import UserSerializer, GroupSerializer
from stocks.models import Listing as SC
from stocks.serializers import ListingSerializer
from stocks.models import BlockDetail
from stocks.serializers import BKDetailSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

@api_view(['GET', 'POST'])
def stockcode_list(request, format=None):
    """
    List all snippets, or create a new snippet.
    """
    if request.method == 'GET':
        values = SC.objects.all()
        serializer = ListingSerializer(values, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ListingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def stockcode_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    try:
        values = SC.objects.get(pk=pk)
    except SC.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ListingSerializer(values)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ListingSerializer(values, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        values.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def ZXG_list(request, format=None):
    """
    List all snippets, or create a new snippet.
    """
    if request.method == 'GET':
        values = BlockDetail.objects.all()
        serializer = BKDetailSerializer(values, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BKDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def ZXG_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    try:
        values = BlockDetail.objects.get(pk=pk)
    except BlockDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BKDetailSerializer(values)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BKDetailSerializer(values, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        values.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
def stockcode_list(request, format=None):
    """
    List all snippets, or create a new snippet.
    """
    if request.method == 'GET':
        values = SC.objects.all()
        serializer = ListingSerializer(values, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ListingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def stockcode_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    try:
        values = SC.objects.get(pk=pk)
    except SC.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ListingSerializer(values)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ListingSerializer(values, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        values.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def BK_list(request, format=None):
    """
    List all snippets, or create a new snippet.
    """
    if request.method == 'GET':
        values = BlockDetail.objects.all()
        serializer = BKDetailSerializer(values, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BKDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def BK_detail(request, pk, format=None):
    """
    Retrieve, update or delete a snippet instance.
    """
    try:
        values = BlockDetail.objects.get(pk=pk)
    except BlockDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BKDetailSerializer(values)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BKDetailSerializer(values, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        values.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
