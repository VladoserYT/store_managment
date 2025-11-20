
import unittest
from datetime import datetime

import sys
from pathlib import Path

# Добавить родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Product, Customer, Order, sort_orders_by_date, sort_orders_by_price


class TestProduct(unittest.TestCase):
    
    def setUp(self):
        """Подготовка к тестам."""
        self.product = Product(1, "Ноутбук", 50000.0, "Мощный ноутбук", 10)
    
    def test_product_creation(self):
        """Тест создания товара."""
        self.assertEqual(self.product.id, 1)
        self.assertEqual(self.product.name, "Ноутбук")
        self.assertEqual(self.product.price, 50000.0)
        self.assertEqual(self.product.quantity, 10)
    
    def test_product_invalid_price(self):
        """Тест на ошибку при отрицательной цене."""
        with self.assertRaises(ValueError):
            Product(2, "Товар", -100.0)
    
    def test_product_invalid_quantity(self):
        """Тест на ошибку при отрицательном количестве."""
        with self.assertRaises(ValueError):
            Product(2, "Товар", 100.0, quantity=-5)
    
    def test_update_quantity(self):
        """Тест обновления количества товара."""
        self.product.update_quantity(5)
        self.assertEqual(self.product.quantity, 15)
        
        self.product.update_quantity(-3)
        self.assertEqual(self.product.quantity, 12)
    
    def test_update_quantity_insufficient(self):
        """Тест на ошибку при недостаточном количестве."""
        with self.assertRaises(ValueError):
            self.product.update_quantity(-20)


class TestCustomer(unittest.TestCase):
    """Тесты для класса Customer."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.customer = Customer(1, "Иван Петров", "ivan@example.com", "+79991234567", "ул. Пушкина, 10")
    
    def test_customer_creation(self):
        """Тест создания клиента."""
        self.assertEqual(self.customer.id, 1)
        self.assertEqual(self.customer.name, "Иван Петров")
        self.assertEqual(self.customer.email, "ivan@example.com")
        self.assertEqual(self.customer.phone, "+79991234567")
    
    def test_invalid_email(self):
        """Тест на ошибку при некорректном email."""
        with self.assertRaises(ValueError):
            Customer(2, "Петр", "invalid-email", "+79991234567")
    
    def test_invalid_phone(self):
        """Тест на ошибку при некорректном телефоне."""
        with self.assertRaises(ValueError):
            Customer(2, "Петр", "petr@example.com", "123")
    
    def test_increment_orders_count(self):
        """Тест увеличения счётчика заказов."""
        self.assertEqual(self.customer.orders_count, 0)
        self.customer.increment_orders_count()
        self.assertEqual(self.customer.orders_count, 1)
        self.customer.increment_orders_count()
        self.assertEqual(self.customer.orders_count, 2)
    
    def test_update_address(self):
        """Тест обновления адреса."""
        new_address = "ул. Лермонтова, 20"
        self.customer.update_address(new_address)
        self.assertEqual(self.customer.address, new_address)


class TestOrder(unittest.TestCase):
    """Тесты для класса Order."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.product1 = Product(1, "Товар 1", 1000.0, quantity=10)
        self.product2 = Product(2, "Товар 2", 2000.0, quantity=5)
        self.order = Order(1, 1)
    
    def test_order_creation(self):
        """Тест создания заказа."""
        self.assertEqual(self.order.id, 1)
        self.assertEqual(self.order.customer_id, 1)
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.total_price, 0)
    
    def test_add_item(self):
        """Тест добавления товара в заказ."""
        self.order.add_item(self.product1, 2)
        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.total_price, 2000.0)
    
    def test_add_multiple_items(self):
        """Тест добавления нескольких товаров."""
        self.order.add_item(self.product1, 2)
        self.order.add_item(self.product2, 1)
        self.assertEqual(len(self.order.items), 2)
        self.assertEqual(self.order.total_price, 4000.0)
    
    def test_add_item_invalid_quantity(self):
        """Тест на ошибку при добавлении товара с неверным количеством."""
        with self.assertRaises(ValueError):
            self.order.add_item(self.product1, 0)
        
        with self.assertRaises(ValueError):
            self.order.add_item(self.product1, -5)
    
    def test_remove_item(self):
        """Тест удаления товара из заказа."""
        self.order.add_item(self.product1, 2)
        self.order.add_item(self.product2, 1)
        
        self.order.remove_item(self.product1.id)
        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.total_price, 2000.0)
    
    def test_set_status(self):
        """Тест изменения статуса заказа."""
        self.order.set_status('processing')
        self.assertEqual(self.order.status, 'processing')
        
        self.order.set_status('shipped')
        self.assertEqual(self.order.status, 'shipped')
    
    def test_set_invalid_status(self):
        """Тест на ошибку при установке неверного статуса."""
        with self.assertRaises(ValueError):
            self.order.set_status('invalid_status')
    
    def test_get_items_count(self):
        """Тест получения общего количества товаров."""
        self.order.add_item(self.product1, 2)
        self.order.add_item(self.product2, 3)
        self.assertEqual(self.order.get_items_count(), 5)


class TestSortingFunctions(unittest.TestCase):
    """Тесты для функций сортировки."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.order1 = Order(1, 1)
        self.order2 = Order(2, 2)
        self.order3 = Order(3, 3)
        
        # Добавить товары
        product1 = Product(1, "Товар 1", 1000.0)
        product2 = Product(2, "Товар 2", 2000.0)
        product3 = Product(3, "Товар 3", 3000.0)
        
        self.order1.add_item(product1, 1)
        self.order2.add_item(product2, 2)
        self.order3.add_item(product3, 1)
    
    def test_sort_orders_by_price_descending(self):
        """Тест сортировки заказов по цене (по убыванию)."""
        orders = [self.order1, self.order2, self.order3]
        sorted_orders = sort_orders_by_price(orders, reverse=True)
        
        # Проверить что заказы отсортированы по убыванию
        self.assertEqual(sorted_orders[0].total_price, 4000.0)  # order2: 2*2000
        self.assertEqual(sorted_orders[1].total_price, 3000.0)  # order3: 1*3000
        self.assertEqual(sorted_orders[2].total_price, 1000.0)  # order1: 1*1000
    
    def test_sort_orders_by_price_ascending(self):
        """Тест сортировки заказов по цене (по возрастанию)."""
        orders = [self.order1, self.order2, self.order3]
        sorted_orders = sort_orders_by_price(orders, reverse=False)
        
        # Проверить что заказы отсортированы по возрастанию
        self.assertEqual(sorted_orders[0].total_price, 1000.0)  # order1: 1*1000
        self.assertEqual(sorted_orders[1].total_price, 3000.0)  # order3: 1*3000
        self.assertEqual(sorted_orders[2].total_price, 4000.0)  # order2: 2*2000


class TestValidation(unittest.TestCase):
    """Тесты для валидации данных."""
    
    def test_email_validation_valid(self):
        """Тест валидации корректного email."""
        try:
            customer = Customer(1, "Тест", "test@example.com", "+79991234567")
            self.assertIsNotNone(customer)
        except ValueError:
            self.fail("Корректный email был отклонён")
    
    def test_email_validation_invalid(self):
        """Тест валидации некорректного email."""
        invalid_emails = [
            "test@",
            "@example.com",
            "test@example",
            "test example@example.com",
            ""
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValueError):
                Customer(1, "Тест", email, "+79991234567")
    
    def test_phone_validation_valid(self):
        """Тест валидации корректного телефона."""
        valid_phones = [
            "+79991234567",
            "+12025551234",
            "79991234567",
            "+1234567890"
        ]
        
        for phone in valid_phones:
            try:
                customer = Customer(1, "Тест", "test@example.com", phone)
                self.assertIsNotNone(customer)
            except ValueError:
                self.fail(f"Корректный телефон {phone} был отклонён")
    
    def test_phone_validation_invalid(self):
        """Тест валидации некорректного телефона."""
        invalid_phones = [
            "123",
            "abc",
            "+0123456789",
            "+012345",
            ""
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(ValueError):
                Customer(1, "Тест", "test@example.com", phone)


if __name__ == '__main__':
    unittest.main()
