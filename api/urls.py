from django.urls import path
from rest_framework_simplejwt.views import *
from .views import *

urlpatterns = [
    path("index/", index, name="index"),
    path("", TaskListCreate.as_view(), name="task-list-create"),
    path("task/<str:pk>/", TaskRetrieveUpdateDestroy.as_view(), name="task_rud"),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', TokenObtainPairView.as_view(), name='login_obtaining_token'),
    path("register/", RegisterView.as_view(), name="register")
]
