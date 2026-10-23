from django.urls import path

from planning import views

app_name = "planning"

urlpatterns = [
    path("monthly/", views.monthly, name="monthly"),
    path(
        "monthly/transactions/<str:kind>/new/",
        views.transaction_create,
        name="transaction_create",
    ),
    path(
        "monthly/transactions/<str:kind>/<int:pk>/edit/",
        views.transaction_edit,
        name="transaction_edit",
    ),
    path(
        "monthly/transactions/<str:kind>/<int:pk>/cancel/",
        views.transaction_cancel,
        name="transaction_cancel",
    ),
    path("budgets/new/", views.budget_create, name="budget_create"),
    path("budgets/<int:pk>/edit/", views.budget_edit, name="budget_edit"),
    path("budgets/<int:pk>/delete/", views.budget_delete, name="budget_delete"),
]
