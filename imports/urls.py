from django.urls import path

from imports import views

app_name = "imports"

urlpatterns = [
    path("", views.upload, name="upload"),
    path("<int:pk>/preview/", views.preview, name="preview"),
    path("<int:pk>/confirm/", views.confirm, name="confirm"),
]
