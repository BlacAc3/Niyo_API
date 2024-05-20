from django.shortcuts import render, get_object_or_404
#rest imports
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
#websocket imports
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
#serializers
from .serializers import TaskSerializer, UserSerializer
from .models import Task

def index(request):
    return render(request, "frontend/index.html")


# API views
class TaskListCreate(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        queryset = Task.objects.filter(userID=request.user.id)
        serializer = TaskSerializer(queryset, many=True)
        if not queryset:
            return Response({"Message":"No task found"}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data["userID"]=request.user.id
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskRetrieveUpdateDestroy(APIView):
    permission_classes=[IsAuthenticated]
    def get_object(self, request, pk):
            return get_object_or_404(Task, uuid=pk, userID=request.user.id)

    def get(self, request, pk):
        instance = self.get_object(request, pk)
        serializer = TaskSerializer(instance)
        return Response(serializer.data)

    def put(self, request, pk):
        instance = self.get_object(request, pk)
        data = request.data.copy()
        data["userID"]=request.user.id #Required to make tasks private to user
        updated_fields = list(data.keys())
        
        #Implement the function such that it doesnt require all arguments be posted to avoid errors
        for field in instance._meta.fields:
            if field.name not in updated_fields:
                data[field.name] = getattr(instance, field.name) #Add default field values to the data
        serializer = TaskSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        instance = self.get_object(request, pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    


#Login and Registration Views
class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        if request.method == "POST":
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

