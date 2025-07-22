import random

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import *


class GenerateUniqueValue:
    def __init__(self, table, dict_columns: dict):
        self.table = table
        self.dict_columns = dict_columns

    def one_generation(self, name_column: str, type_column):
        len_str = 15
        min_int = 1000
        max_int = 10000
        if type_column == str():
            while True:
                text = "".join(
                    [
                        random.choice("abc123" if i != 5 else "ABC")
                        for i in range(len_str)
                    ]
                )
                if not self.table.objects.filter(**{name_column: text}).first():
                    break
            return text
        elif type_column == int():
            while True:
                number = random.randint(min_int, max_int)
                if not self.table.objects.filter(**{name_column: number}).first():
                    break
            return number
        else:
            raise TypeError("Неправильный тип данных в функции one_generation")

    def generate(self) -> dict:
        result_dict = {}
        for column_name, type_column in self.dict_columns.items():
            unique_value = self.one_generation(
                name_column=column_name, type_column=type_column
            )
            result_dict[column_name] = unique_value
        return result_dict


class AuthUserClass:
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token_and_created = Token.objects.get_or_create(user=self.user)
        self.token_prefix = "token "
        self.token = self.token_prefix + str(self.token_and_created[0])
        self.client.credentials(HTTP_AUTHORIZATION=self.token)


class PatternTest(AuthUserClass):
    table = None  # Таблица для теста
    table_name = (
        None  # Название маршрута к таблице в api (без -list или -detail на конце)
    )
    table_parameters = {}  # Параметры для создания объекта таблицы
    table_edit_parameters = (
        {}
    )  # Параметры для теста редактирования определенного объекта таблицы
    table_unique_columns = (
        {}
    )  # Уникальные столбцы в таблице в формате СТОЛБЕЦ:ТИП ЗНАЧЕНИЯ
    auth_test = False  # Нужно ли делать тест с авторизацией или нет
    table_foreigns_obj = (
        {}
    )  # Объекты всех связанных и необходимых других таблиц | УКАЗЫВАЕТСЯ В МЕТОДЕ setUp

    table_foreigns_id = (
        {}
    )  # Айди объектов всех связанных и необходимых других таблиц | СОЗДАЕТСЯ АВТОМАТИЧЕСКИ
    obj_unique_generate = (
        None  # Объект класса GenerateUniqueValue | СОЗДАЕТСЯ АВТОМАТИЧЕСК
    )

    def setUp(self):
        if self.auth_test:
            super().setUp()

        self.obj_unique_generate = GenerateUniqueValue(
            table=self.table, dict_columns=self.table_unique_columns
        )
        unique_parameters = self.obj_unique_generate.generate()

        self.table_foreigns_id = {
            key: value.id for key, value in self.table_foreigns_obj.items()
        }

        self.start_table = self.table.objects.create(
            **(self.table_parameters | self.table_foreigns_obj | unique_parameters)
        )
        self.table_id = self.start_table.id
        self.url_detail = reverse(
            f"{self.table_name}-detail", kwargs={"pk": self.table_id}
        )
        self.url_all = reverse(f"{self.table_name}-list")

    def test_create_table(self):
        unique_parameters = self.obj_unique_generate.generate()
        data = self.table_parameters | self.table_foreigns_id | unique_parameters
        old_count_obj = self.table.objects.count()
        response = self.client.post(self.url_all, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.table.objects.count() > old_count_obj)

    def test_get_all_table(self):
        response = self.client.get(self.url_all)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail_table(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_table(self):
        data = self.table_edit_parameters
        response = self.client.patch(self.url_detail, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.start_table = self.table.objects.filter(
            id=self.table_id
        ).first()  # ДЕЛАЕМ ТЕКУЩИЙ ОБЪЕКТ В ПОЛЕ АКТУАЛЬНЫМ
        for parameter_name in self.table_edit_parameters.keys():
            self.assertEqual(
                model_to_dict(self.start_table)[parameter_name], data[parameter_name]
            )

    def test_remove_table(self):
        unique_parameters = self.obj_unique_generate.generate()
        new_table = self.table.objects.create(
            **(self.table_parameters | self.table_foreigns_obj | unique_parameters)
        )
        new_url_detail = reverse(
            f"{self.table_name}-detail", kwargs={"pk": new_table.id}
        )
        response = self.client.delete(new_url_detail)
        delete_category = self.table.objects.filter(id=new_table.id).first()
        self.assertIsNone(delete_category)


class CategoryTest(PatternTest, APITestCase):
    table = Category
    table_name = "category"
    table_parameters = {"name": "Имя категории для теста"}
    table_edit_parameters = {"name": "Имя категории для теста изменения"}
    auth_test = True


class SupplierTest(PatternTest, APITestCase):
    table = Supplier
    table_name = "supplier"
    table_parameters = {"name": "Тестовый поставщик"}
    table_edit_parameters = {"name": "Измененное имя"}
    auth_test = True

    def setUp(self):
        category = Category.objects.create(name="Категория для теста")
        self.table_foreigns_obj["category"] = category
        super().setUp()


class ProductTest(PatternTest, APITestCase):
    table = Product
    table_name = "product"
    table_parameters = {"name": "Тестовый продукт", "price": 100}
    table_unique_columns = {"sku": int()}
    table_edit_parameters = {"name": "Измененное имя"}
    auth_test = True

    def setUp(self):
        category = Category.objects.create(name="категория")
        supplier = Supplier.objects.create(name="поставщик", category=category)
        self.table_foreigns_obj["supplier"] = supplier
        super().setUp()


class StockMovementTest(PatternTest, APITestCase):
    table = StockMovement
    table_name = "stockmovement"
    table_parameters = {
        "operator_email": "testemail@gmail.com",
        "quantity": 100,
        "note": "тестовое описание транзакции",
    }
    table_edit_parameters = {"note": "новое тестовое описание"}
    auth_test = True

    def setUp(self):
        category = Category.objects.create(name="категория")
        supplier = Supplier.objects.create(name="поставщик", category=category)
        unique_sku = GenerateUniqueValue(table=Product, dict_columns={}).one_generation(
            name_column="sku", type_column=int()
        )
        product = Product.objects.create(
            name="продукт", supplier=supplier, sku=unique_sku, price=100
        )
        self.table_foreigns_obj["product"] = product
        super().setUp()
