from django.urls import path

from planning import views

app_name = "planning"

urlpatterns = [
    path("monthly/", views.monthly, name="monthly"),
    path("budgets/new/", views.budget_create, name="budget_create"),
]
