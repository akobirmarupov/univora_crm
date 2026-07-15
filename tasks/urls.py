from django.urls import path

from tasks.routes.tasks_view import TaskListAPIView, TaskDetailAPIView
from tasks.routes.activity_view import ActivaListAPIView, ActivityDetailAPIView

urlpatterns = [
    path("tasks/", TaskListAPIView.as_view(), name="tasks-list"),
    path("tasks/<int:pk>/", TaskDetailAPIView.as_view(), name="tasks-detail"),

    path("activy/", ActivaListAPIView.as_view(), name="activy-list"),
    path("activy/<int:pk>/", ActivityDetailAPIView.as_view(), name="activy-detail"),
]