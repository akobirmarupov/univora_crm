from django.urls import path

from tasks.routes.tasks_view import TaskListAPIView, TaskDetailAPIView


urlpatterns = [
    path("tasks/", TaskListAPIView.as_view(), name="tasks-list"),
    path("tasks/<int:pk>/", TaskDetailAPIView.as_view(), name="tasks-detail"),
]