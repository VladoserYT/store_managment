"""
Модуль test_analysis.py - Unit-тесты для анализа данных.

Этот модуль содержит тесты для функций анализа и визуализации.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Добавить родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Product, Customer, Order
from db import DatabaseManager
from analysis import DataAnalyzer


class TestDataAnalyzer(unittest.TestCase):
    """Тесты для класса DataAnalyzer."""
    
    def setUp(self):
        """Подготовка к тестам."""
        # Создать временную БД
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        
        self.db = DatabaseManager(str(self.db_path))
        self.analyzer = DataAnalyzer(self.db)
        
        # Добавить тестовые данные
        self._add_test_data()
    
    def tearDown(self):
        """Очистка после тестов."""
        shutil.rmtree(self.temp_dir)
    
    def _add_test_data(self):
        """Добавить тестовые данные в БД."""
        # Добавить товары
        product1 = Product(0, "Товар 1", 1000.0, "Описание 1", 10)
        product2 = Product(0, "Товар 2", 2000.0, "Описание 2", 5)
        product3 = Product(0, "Товар 3", 3000.0, "Описание 3", 15)
        
        self.db.add_product(product1)
        self.db.add_product(product2)
        self.db.add_product(product3)
        
        # Добавить клиентов
        customer1 = Customer(0, "Клиент 1", "client1@example.com", "+79991111111", "Адрес 1")
        customer2 = Customer(0, "Клиент 2", "client2@example.com", "+79992222222", "Адрес 2")
        
        self.db.add_customer(customer1)
        self.db.add_customer(customer2)
        
        # Добавить заказы
        order1 = Order(0, 1)
        order1.add_item(product1, 2)
        order1.add_item(product2, 1)
        self.db.add_order(order1)
        
        order2 = Order(0, 2)
        order2.add_item(product2, 3)
        self.db.add_order(order2)
        
        order3 = Order(0, 1)
        order3.add_item(product3, 1)
        self.db.add_order(order3)
    
    def test_get_sales_by_date(self):
        """Тест получения продаж по датам."""
        df = self.analyzer.get_sales_by_date()
        
        self.assertFalse(df.empty)
        self.assertIn('date', df.columns)
        self.assertIn('total', df.columns)
        self.assertIn('items', df.columns)
    
    def test_get_top_customers(self):
        """Тест получения топовых клиентов."""
        df = self.analyzer.get_top_customers(5)
        
        self.assertFalse(df.empty)
        self.assertIn('name', df.columns)
        self.assertIn('orders', df.columns)
        
        # Проверить, что клиент с наибольшим количеством заказов первый
        self.assertEqual(df.iloc[0]['orders'], 2)
    
    def test_get_top_products(self):
        """Тест получения топовых товаров."""
        df = self.analyzer.get_top_products(5)
        
        self.assertFalse(df.empty)
        self.assertIn('name', df.columns)
        self.assertIn('quantity', df.columns)
        self.assertIn('revenue', df.columns)
    
    def test_get_order_status_distribution(self):
        """Тест получения распределения статусов."""
        df = self.analyzer.get_order_status_distribution()
        
        self.assertFalse(df.empty)
        self.assertIn('status', df.columns)
        self.assertIn('count', df.columns)
        
        # Все заказы должны быть в статусе 'pending'
        self.assertEqual(df[df['status'] == 'pending'].iloc[0]['count'], 3)
    
    def test_get_summary_statistics(self):
        """Тест получения сводной статистики."""
        stats = self.analyzer.get_summary_statistics()
        
        self.assertEqual(stats['total_products'], 3)
        self.assertEqual(stats['total_customers'], 2)
        self.assertEqual(stats['total_orders'], 3)
        self.assertGreater(stats['total_revenue'], 0)
        self.assertGreater(stats['avg_order_value'], 0)
        self.assertGreater(stats['total_items_sold'], 0)
    
    def test_plot_sales_dynamics(self):
        """Тест построения графика динамики продаж."""
        output_file = self.analyzer.plot_sales_dynamics()
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(output_file.endswith('.png'))
    
    def test_plot_top_customers(self):
        """Тест построения графика топовых клиентов."""
        output_file = self.analyzer.plot_top_customers(5)
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(output_file.endswith('.png'))
    
    def test_plot_top_products(self):
        """Тест построения графика топовых товаров."""
        output_file = self.analyzer.plot_top_products(5)
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(output_file.endswith('.png'))
    
    def test_plot_order_status_distribution(self):
        """Тест построения графика распределения статусов."""
        output_file = self.analyzer.plot_order_status_distribution()
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(output_file.endswith('.png'))


class TestDatabaseManager(unittest.TestCase):
    """Тесты для класса DatabaseManager."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = DatabaseManager(str(self.db_path))
    
    def tearDown(self):
        """Очистка после тестов."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_and_get_product(self):
        """Тест добавления и получения товара."""
        product = Product(0, "Тестовый товар", 100.0, "Описание", 5)
        product_id = self.db.add_product(product)
        
        retrieved = self.db.get_product(product_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Тестовый товар")
        self.assertEqual(retrieved.price, 100.0)
    
    def test_add_and_get_customer(self):
        """Тест добавления и получения клиента."""
        customer = Customer(0, "Тест", "test@example.com", "+79991234567", "Адрес")
        customer_id = self.db.add_customer(customer)
        
        retrieved = self.db.get_customer(customer_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Тест")
        self.assertEqual(retrieved.email, "test@example.com")
    
    def test_duplicate_customer_email(self):
        """Тест на ошибку при добавлении клиента с дублирующимся email."""
        customer1 = Customer(0, "Тест 1", "test@example.com", "+79991111111", "Адрес 1")
        customer2 = Customer(0, "Тест 2", "test@example.com", "+79992222222", "Адрес 2")
        
        self.db.add_customer(customer1)
        result = self.db.add_customer(customer2)
        
        self.assertEqual(result, -1)
    
    def test_export_import_csv(self):
        """Тест экспорта и импорта CSV."""
        # Добавить данные
        product = Product(0, "Товар", 100.0, "Описание", 5)
        self.db.add_product(product)
        
        customer = Customer(0, "Клиент", "client@example.com", "+79991234567", "Адрес")
        self.db.add_customer(customer)
        
        # Экспортировать
        export_dir = Path(self.temp_dir) / "export"
        export_dir.mkdir()
        self.db.export_to_csv(str(export_dir))
        
        # Проверить файлы
        self.assertTrue((export_dir / "products.csv").exists())
        self.assertTrue((export_dir / "customers.csv").exists())
        self.assertTrue((export_dir / "orders.csv").exists())
    
    def test_export_import_json(self):
        """Тест экспорта и импорта JSON."""
        # Добавить данные
        product = Product(0, "Товар", 100.0, "Описание", 5)
        self.db.add_product(product)
        
        customer = Customer(0, "Клиент", "client@example.com", "+79991234567", "Адрес")
        self.db.add_customer(customer)
        
        # Экспортировать
        export_dir = Path(self.temp_dir) / "export"
        export_dir.mkdir()
        self.db.export_to_json(str(export_dir))
        
        # Проверить файлы
        self.assertTrue((export_dir / "products.json").exists())
        self.assertTrue((export_dir / "customers.json").exists())
        self.assertTrue((export_dir / "orders.json").exists())


if __name__ == '__main__':
    unittest.main()
