from django.urls import path
from .import_of_goods import PartnerUpdate
from .views import RegisterAPI, LoginAPI

app_name = "orders"

urlpatterns = [
    path(
        "partner/update/", PartnerUpdate.as_view(), name="partner-update"
    ),  # импорт товаров
    path(
        "register/", RegisterAPI.as_view(), name="register"
    ),  # регистрация пользователя
    path("login/", LoginAPI.as_view(), name="login"),  # вход пользователя
]
