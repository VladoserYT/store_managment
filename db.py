"""
Модуль db.py - Работа с базой данных SQLite и импорт/экспорт данных.

Этот модуль предоставляет функции для:
- Создания и инициализации БД
- CRUD операций с товарами, клиентами и заказами
- Импорта и экспорта данных в/из CSV и JSON форматов
"""

import sqlite3
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from models import Product, Customer, Order


class DatabaseManager:
    """
    Менеджер для работы с SQLite базой данных.
    
    Демонстрирует инкапсуляцию и управление ресурсами.
    """
    
    def __init__(self, db_path: str = "data/store.db"):
        """
        Инициализация менеджера БД.
        
        Parameters
        ----------
        db_path : str
            Путь к файлу БД SQLite
        """
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Получить соединение с БД.
        
        Returns
        -------
        sqlite3.Connection
            Соединение с БД
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self) -> None:
        """Инициализировать таблицы БД при первом запуске."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    description TEXT,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица клиентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    address TEXT,
                    orders_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    total_price REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            ''')
            
            # Таблица товаров в заказах (связь многие-ко-многим)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при инициализации БД: {e}")
        finally:
            conn.close()
    
    # ============ ТОВАРЫ ============
    
    def add_product(self, product: Product) -> int:
        """
        Добавить товар в БД.
        
        Parameters
        ----------
        product : Product
            Объект товара
            
        Returns
        -------
        int
            ID добавленного товара
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (name, price, description, quantity)
                VALUES (?, ?, ?, ?)
            ''', (product.name, product.price, product.description, product.quantity))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении товара: {e}")
            return -1
        finally:
            conn.close()
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """
        Получить товар по ID.
        
        Parameters
        ----------
        product_id : int
            ID товара
            
        Returns
        -------
        Optional[Product]
            Объект товара или None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            
            if row:
                return Product(
                    product_id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    description=row['description'],
                    quantity=row['quantity']
                )
            return None
        finally:
            conn.close()
    
    def get_all_products(self) -> List[Product]:
        """
        Получить все товары.
        
        Returns
        -------
        List[Product]
            Список всех товаров
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM products')
            rows = cursor.fetchall()
            
            return [
                Product(
                    product_id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    description=row['description'],
                    quantity=row['quantity']
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def update_product_quantity(self, product_id: int, new_quantity: int) -> bool:
        """
        Обновить количество товара.
        
        Parameters
        ----------
        product_id : int
            ID товара
        new_quantity : int
            Новое количество
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE products SET quantity = ? WHERE id = ?',
                (new_quantity, product_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении товара: {e}")
            return False
        finally:
            conn.close()
    
    def delete_product(self, product_id: int) -> bool:
        """
        Удалить товар.
        
        Parameters
        ----------
        product_id : int
            ID товара
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении товара: {e}")
            return False
        finally:
            conn.close()
    
    # ============ КЛИЕНТЫ ============
    
    def add_customer(self, customer: Customer) -> int:
        """
        Добавить клиента в БД.
        
        Parameters
        ----------
        customer : Customer
            Объект клиента
            
        Returns
        -------
        int
            ID добавленного клиента
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO customers (name, email, phone, address, orders_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer.name, customer.email, customer.phone, customer.address, 0))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Ошибка: клиент с email {customer.email} уже существует")
            return -1
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении клиента: {e}")
            return -1
        finally:
            conn.close()
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """
        Получить клиента по ID.
        
        Parameters
        ----------
        customer_id : int
            ID клиента
            
        Returns
        -------
        Optional[Customer]
            Объект клиента или None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            row = cursor.fetchone()
            
            if row:
                customer = Customer(
                    customer_id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    address=row['address']
                )
                customer._orders_count = row['orders_count']
                return customer
            return None
        finally:
            conn.close()
    
    def get_all_customers(self) -> List[Customer]:
        """
        Получить всех клиентов.
        
        Returns
        -------
        List[Customer]
            Список всех клиентов
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM customers')
            rows = cursor.fetchall()
            
            customers = []
            for row in rows:
                customer = Customer(
                    customer_id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    address=row['address']
                )
                customer._orders_count = row['orders_count']
                customers.append(customer)
            
            return customers
        finally:
            conn.close()
    
    def update_customer_address(self, customer_id: int, new_address: str) -> bool:
        """
        Обновить адрес клиента.
        
        Parameters
        ----------
        customer_id : int
            ID клиента
        new_address : str
            Новый адрес
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE customers SET address = ? WHERE id = ?',
                (new_address, customer_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении клиента: {e}")
            return False
        finally:
            conn.close()
    
    def increment_customer_orders(self, customer_id: int) -> bool:
        """
        Увеличить счётчик заказов клиента.
        
        Parameters
        ----------
        customer_id : int
            ID клиента
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE customers SET orders_count = orders_count + 1 WHERE id = ?',
                (customer_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении счётчика заказов: {e}")
            return False
        finally:
            conn.close()
    
    def delete_customer(self, customer_id: int) -> bool:
        """
        Удалить клиента.
        
        Parameters
        ----------
        customer_id : int
            ID клиента
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении клиента: {e}")
            return False
        finally:
            conn.close()
    
    # ============ ЗАКАЗЫ ============
    
    def add_order(self, order: Order) -> int:
        """
        Добавить заказ в БД.
        
        Parameters
        ----------
        order : Order
            Объект заказа
            
        Returns
        -------
        int
            ID добавленного заказа
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO orders (customer_id, status, total_price)
                VALUES (?, ?, ?)
            ''', (order.customer_id, order.status, order.total_price))
            
            order_id = cursor.lastrowid
            
            # Добавить товары в заказ
            for product, quantity in order.items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity)
                    VALUES (?, ?, ?)
                ''', (order_id, product.id, quantity))
            
            # Увеличить счётчик заказов клиента
            self.increment_customer_orders(order.customer_id)
            
            conn.commit()
            return order_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении заказа: {e}")
            return -1
        finally:
            conn.close()
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """
        Получить заказ по ID.
        
        Parameters
        ----------
        order_id : int
            ID заказа
            
        Returns
        -------
        Optional[Order]
            Объект заказа или None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            order = Order(
                order_id=row['id'],
                customer_id=row['customer_id']
            )
            order._status = row['status']
            order._total_price = row['total_price']
            
            # Получить товары в заказе
            cursor.execute('''
                SELECT p.*, oi.quantity FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            ''', (order_id,))
            
            for item_row in cursor.fetchall():
                product = Product(
                    product_id=item_row['id'],
                    name=item_row['name'],
                    price=item_row['price'],
                    description=item_row['description'],
                    quantity=item_row['quantity']
                )
                order._items.append((product, item_row['quantity']))
            
            return order
        finally:
            conn.close()
    
    def get_all_orders(self) -> List[Order]:
        """
        Получить все заказы.
        
        Returns
        -------
        List[Order]
            Список всех заказов
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT DISTINCT id FROM orders')
            order_ids = [row['id'] for row in cursor.fetchall()]
            
            return [self.get_order(order_id) for order_id in order_ids if self.get_order(order_id)]
        finally:
            conn.close()
    
    def get_customer_orders(self, customer_id: int) -> List[Order]:
        """
        Получить все заказы клиента.
        
        Parameters
        ----------
        customer_id : int
            ID клиента
            
        Returns
        -------
        List[Order]
            Список заказов клиента
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM orders WHERE customer_id = ?', (customer_id,))
            order_ids = [row['id'] for row in cursor.fetchall()]
            
            return [self.get_order(order_id) for order_id in order_ids if self.get_order(order_id)]
        finally:
            conn.close()
    
    def update_order_status(self, order_id: int, new_status: str) -> bool:
        """
        Обновить статус заказа.
        
        Parameters
        ----------
        order_id : int
            ID заказа
        new_status : str
            Новый статус
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE orders SET status = ? WHERE id = ?',
                (new_status, order_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении статуса заказа: {e}")
            return False
        finally:
            conn.close()
    
    def delete_order(self, order_id: int) -> bool:
        """
        Удалить заказ.
        
        Parameters
        ----------
        order_id : int
            ID заказа
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении заказа: {e}")
            return False
        finally:
            conn.close()
    
    # ============ ИМПОРТ/ЭКСПОРТ ============
    
    def export_to_csv(self, export_dir: str = "data") -> Dict[str, str]:
        """
        Экспортировать данные в CSV файлы.
        
        Parameters
        ----------
        export_dir : str
            Директория для экспорта
            
        Returns
        -------
        Dict[str, str]
            Словарь с путями к экспортированным файлам
        """
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        files = {}
        
        try:
            # Экспорт товаров
            products_file = Path(export_dir) / "products.csv"
            with open(products_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Название', 'Цена', 'Описание', 'Количество'])
                for product in self.get_all_products():
                    writer.writerow([
                        product.id, product.name, product.price,
                        product.description, product.quantity
                    ])
            files['products'] = str(products_file)
            
            # Экспорт клиентов
            customers_file = Path(export_dir) / "customers.csv"
            with open(customers_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Имя', 'Email', 'Телефон', 'Адрес', 'Количество заказов'])
                for customer in self.get_all_customers():
                    writer.writerow([
                        customer.id, customer.name, customer.email,
                        customer.phone, customer.address, customer.orders_count
                    ])
            files['customers'] = str(customers_file)
            
            # Экспорт заказов
            orders_file = Path(export_dir) / "orders.csv"
            with open(orders_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'ID Клиента', 'Статус', 'Общая стоимость', 'Дата создания'])
                for order in self.get_all_orders():
                    writer.writerow([
                        order.id, order.customer_id, order.status,
                        order.total_price, order.created_at
                    ])
            files['orders'] = str(orders_file)
            
            print(f"✓ Данные успешно экспортированы в {export_dir}")
            return files
        except Exception as e:
            print(f"Ошибка при экспорте в CSV: {e}")
            return {}
    
    def export_to_json(self, export_dir: str = "data") -> Dict[str, str]:
        """
        Экспортировать данные в JSON файлы.
        
        Parameters
        ----------
        export_dir : str
            Директория для экспорта
            
        Returns
        -------
        Dict[str, str]
            Словарь с путями к экспортированным файлам
        """
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        files = {}
        
        try:
            # Экспорт товаров
            products_file = Path(export_dir) / "products.json"
            products_data = [
                {
                    'id': p.id,
                    'name': p.name,
                    'price': p.price,
                    'description': p.description,
                    'quantity': p.quantity
                }
                for p in self.get_all_products()
            ]
            with open(products_file, 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)
            files['products'] = str(products_file)
            
            # Экспорт клиентов
            customers_file = Path(export_dir) / "customers.json"
            customers_data = [
                {
                    'id': c.id,
                    'name': c.name,
                    'email': c.email,
                    'phone': c.phone,
                    'address': c.address,
                    'orders_count': c.orders_count
                }
                for c in self.get_all_customers()
            ]
            with open(customers_file, 'w', encoding='utf-8') as f:
                json.dump(customers_data, f, ensure_ascii=False, indent=2)
            files['customers'] = str(customers_file)
            
            # Экспорт заказов
            orders_file = Path(export_dir) / "orders.json"
            orders_data = [
                {
                    'id': o.id,
                    'customer_id': o.customer_id,
                    'status': o.status,
                    'total_price': o.total_price,
                    'items_count': o.get_items_count(),
                    'created_at': o.created_at.isoformat()
                }
                for o in self.get_all_orders()
            ]
            with open(orders_file, 'w', encoding='utf-8') as f:
                json.dump(orders_data, f, ensure_ascii=False, indent=2)
            files['orders'] = str(orders_file)
            
            print(f"✓ Данные успешно экспортированы в {export_dir}")
            return files
        except Exception as e:
            print(f"Ошибка при экспорте в JSON: {e}")
            return {}
    
    def import_from_csv(self, csv_dir: str = "data") -> bool:
        """
        Импортировать данные из CSV файлов.
        
        Parameters
        ----------
        csv_dir : str
            Директория с CSV файлами
            
        Returns
        -------
        bool
            True если успешно, False иначе
        """
        try:
            # Импорт товаров
            products_file = Path(csv_dir) / "products.csv"
            if products_file.exists():
                with open(products_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            product = Product(
                                product_id=int(row['ID']),
                                name=row['Название'],
                                price=float(row['Цена']),
                                description=row['Описание'],
                                quantity=int(row['Количество'])
                            )
                            self.add_product(product)
                        except (ValueError, KeyError) as e:
                            print(f"Ошибка при импорте товара: {e}")
            
            # Импорт клиентов
            customers_file = Path(csv_dir) / "customers.csv"
            if customers_file.exists():
                with open(customers_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            customer = Customer(
                                customer_id=int(row['ID']),
                                name=row['Имя'],
                                email=row['Email'],
                                phone=row['Телефон'],
                                address=row['Адрес']
                            )
                            self.add_customer(customer)
                        except (ValueError, KeyError) as e:
                            print(f"Ошибка при импорте клиента: {e}")
            
            print(f"✓ Данные успешно импортированы из {csv_dir}")
            return True
        except Exception as e:
            print(f"Ошибка при импорте из CSV: {e}")
            return False
