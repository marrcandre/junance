from django.urls import path

from investments import views

app_name = "investments"

urlpatterns = [
    path("", views.position_list, name="position_list"),
]
