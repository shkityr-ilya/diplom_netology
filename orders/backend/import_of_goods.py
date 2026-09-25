from django.db import transaction
import requests
import yaml
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.core.validators import URLValidator
from .models import Category, ProductInfo, Product, ProductParameter, Shop, Parameter


class PartnerUpdate(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type != "shop":
            return Response(
                {"Status": False, "Error": "Требуется авторизация магазина"},
                status=status.HTTP_403_FORBIDDEN,
            )

        url = request.data.get("url", "").strip()
        if not url:
            return Response(
                {"Status": False, "Error": "Не указан URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError as e:
            return Response(
                {"Status": False, "Error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = yaml.safe_load(response.content)
        except requests.RequestException as e:
            return Response(
                {"Status": False, "Error": f"Ошибка загрузки файла: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except yaml.YAMLError as e:
            return Response(
                {"Status": False, "Error": f"Ошибка парсинга YAML: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        required_keys = ["shop", "categories", "goods"]
        if not all(key in data for key in required_keys):
            return Response(
                {"Status": False, "Error": "Неверная структура входящего файла"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            shop, _ = Shop.objects.get_or_create(
                name=data["shop"], user_id=request.user.id
            )
            for category_data in data["categories"]:
                category_object, created = Category.objects.update_or_create(
                    id=category_data["id"], defaults={"name": category_data["name"]}
                )
                category_object.shops.add(shop)
            current_external_ids = [item["id"] for item in data["goods"]]
            ProductInfo.objects.filter(shop=shop).exclude(
                external_id__in=current_external_ids
            ).delete()
            for item in data["goods"]:
                product, _ = Product.objects.get_or_create(
                    name=item["name"], category_id=item["category"]
                )
                product_info_defaults = {
                    "model": item["model"],
                    "price": item["price"],
                    "price_rrc": item["price_rrc"],
                    "quantity": item["quantity"],
                    "shop": shop,
                }
                product_info, created = ProductInfo.objects.update_or_create(
                    external_id=item["id"],
                    product=product,
                    defaults=product_info_defaults,
                )
                product_info.parameters.all().delete()
                for name, value in item["parameters"].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(
                        product_info=product_info,
                        parameter=parameter_object,
                        value=value,
                    )
        return Response({"Status": True})
