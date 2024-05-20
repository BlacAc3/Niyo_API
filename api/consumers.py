import json
import jwt
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.db import close_old_connections
from .models import Task
from .serializers import TaskSerializer
from django.shortcuts import get_object_or_404
from json.decoder import JSONDecodeError

class TaskConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()  # Accept connection initially to receive the token

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except JSONDecodeError as e:
            await self.send(text_data=json.dumps({"message": "Invalid JSON", "error": str(e)}))
            await self.close(code=4003)
            return
        
        if 'type' in data and data['type'] == 'auth':
            self.user = None

            # Expect the first message to contain the token    
            token = data.get('token')
            if token:
                user = await self.get_user_from_token(token)
                if user:
                    self.user = user
                    self.group_name = f"tasks"
                    await self.channel_layer.group_add(self.group_name, self.channel_name)
                    await self.send(text_data=json.dumps({"message": "Authentication successful"}))
                    return
                else:
                    await self.send(text_data=json.dumps({"message":"Token Invalid"}))
                    await self.close(code=4001)
                    return 
            else:
                await self.send(text_data=json.dumps({"message":"JWT Token Not Found"}))
                return
            

        elif self.scope["user"]:
            tasks = ""
            # Handle messages after authentication
            try:
                if data["mode"] == "all":
                    tasks = await self.get_tasks()
                elif data["mode"] == "create":
                    tasks = await self.create_task(data["data"])
                elif data["mode"] == "read":
                    tasks = await self.get_task(data["task_id"])
                elif data["mode"] == "update":
                    tasks = await self.update_task(id=data["task_id"], data=data["data"])
                elif data["mode"] == "delete":
                    tasks = await self.delete_task(id=data["task_id"])
            except KeyError as e:
                await self.send(text_data=json.dumps({"message":"Invalid JSON DATA"}))
                return

            await self.channel_layer.group_send(self.group_name, {
                'type': 'task.update',
                'task': tasks  # Send serialized task data
            })

    async def task_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task.update',
            'task': event['task']
        }))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            UntypedToken(token)
            decoded_data = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded_data["user_id"]
            user = User.objects.get(id=user_id)
            return user
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def get_tasks(self):
        queryset = Task.objects.filter(user_id=self.user.id)
        serializer = TaskSerializer(queryset, many=True)
        if not queryset:
            return json.dumps({"message": "No task found"})
        return serializer.data

    @database_sync_to_async
    def create_task(self, json_data):
        json_data["user_id"] = self.user.id
        serializer = TaskSerializer(data=json_data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        return serializer.errors


    @database_sync_to_async
    def get_task(self, id):
        instance = Task.objects.get(uuid=id)
        print(instance.user_id)
        serializer = TaskSerializer(instance)
        return serializer.data

    @database_sync_to_async
    def update_task(self, id, data):
        instance = Task.objects.get(uuid=id)
        data["user_id"] = self.user.id  # Required to make tasks private to user
        updated_fields = list(data.keys())
        
        for field in instance._meta.fields:
            if field.name not in updated_fields:
                data[field.name] = getattr(instance, field.name)  # Add default field values to the data
        serializer = TaskSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        return serializer.errors
    @database_sync_to_async
    def delete_task(self, id):
        instance = Task.objects.get(uuid=id)
        if not instance:
            return {"message": "Task not Found!"}
        instance.delete()
        return {"message": "Task deleted!"}


    #json format
    #json = {
    #     "mode":"all", 
    #     "task_id":"1",
    #     "data":{
    #         "task":"lorem",
    #         "description":"ipsum"
    #         }
    #}