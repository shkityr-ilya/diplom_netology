from django.urls import path
from .import_of_goods import PartnerUpdate

app_name = "orders"

urlpatterns = [
    path(
        "partner/update/", PartnerUpdate.as_view(), name="partner-update"
    ),  # импорт товаров
]
