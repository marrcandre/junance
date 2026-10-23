from django.urls import path

from cards import views

app_name = "cards"

urlpatterns = [
    path("", views.card_list, name="card_list"),
    path("purchases/new/", views.purchase_create, name="purchase_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
]
