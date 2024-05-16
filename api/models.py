from django.db import models
import uuid
from django.contrib.auth.models import User
# Create your models here.

class Task(models.Model):
    userID = models.IntegerField()
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    task = models.CharField(max_length=100)
    description = models.TextField(default=None)