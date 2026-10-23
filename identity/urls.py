from django.urls import path

from identity import views

app_name = "identity"

urlpatterns = [
    path("", views.family_list, name="family_list"),
    path("new/", views.family_create, name="family_create"),
]
