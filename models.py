"""
Модуль models.py - Классы данных для интернет-магазина.

Этот модуль содержит классы для представления основных сущностей:
- Product: товар с названием, ценой и описанием
- Customer: клиент с контактными данными и валидацией
- Order: заказ с товарами и статусом

Демонстрирует применение ООП: инкапсуляция, наследование и полиморфизм.
"""

import re
from datetime import datetime
from typing import List, Optional


class BaseEntity:
    """
    Базовый класс для всех сущностей.
    
    Демонстрирует инкапсуляцию и наследование.
    """
    
    def __init__(self, entity_id: int):
        """
        Инициализация базовой сущности.
        
        Parameters
        ----------
        entity_id : int
            Уникальный идентификатор сущности
        """
        self._id = entity_id
        self._created_at = datetime.now()
    
    @property
    def id(self) -> int:
        """Получить ID сущности (read-only)."""
        return self._id
    
    @property
    def created_at(self) -> datetime:
        """Получить дату создания (read-only)."""
        return self._created_at
    
    def __repr__(self) -> str:
        """Строковое представление сущности."""
        return f"{self.__class__.__name__}(id={self._id})"


class Product(BaseEntity):
    """
    Класс для представления товара.
    
    Attributes
    ----------
    name : str
        Название товара
    price : float
        Цена товара в рублях
    description : str
        Описание товара
    quantity : int
        Количество товара на складе
    """
    
    def __init__(self, product_id: int, name: str, price: float, 
                 description: str = "", quantity: int = 0):
        """
        Инициализация товара.
        
        Parameters
        ----------
        product_id : int
            Уникальный идентификатор товара
        name : str
            Название товара
        price : float
            Цена товара (должна быть > 0)
        description : str, optional
            Описание товара
        quantity : int, optional
            Количество на складе (по умолчанию 0)
            
        Raises
        ------
        ValueError
            Если цена <= 0 или количество < 0
        """
        super().__init__(product_id)
        
        if price <= 0:
            raise ValueError("Цена товара должна быть больше 0")
        if quantity < 0:
            raise ValueError("Количество товара не может быть отрицательным")
        
        self._name = name
        self._price = price
        self._description = description
        self._quantity = quantity
    
    @property
    def name(self) -> str:
        """Получить название товара."""
        return self._name
    
    @property
    def price(self) -> float:
        """Получить цену товара."""
        return self._price
    
    @property
    def description(self) -> str:
        """Получить описание товара."""
        return self._description
    
    @property
    def quantity(self) -> int:
        """Получить количество товара на складе."""
        return self._quantity
    
    def update_quantity(self, delta: int) -> None:
        """
        Изменить количество товара на складе.
        
        Parameters
        ----------
        delta : int
            Изменение количества (может быть отрицательным)
            
        Raises
        ------
        ValueError
            Если результирующее количество будет отрицательным
        """
        new_quantity = self._quantity + delta
        if new_quantity < 0:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {self._quantity}")
        self._quantity = new_quantity
    
    def __repr__(self) -> str:
        """Строковое представление товара."""
        return f"Product(id={self._id}, name='{self._name}', price={self._price}, qty={self._quantity})"


class Customer(BaseEntity):
    """
    Класс для представления клиента.
    
    Демонстрирует валидацию данных через регулярные выражения.
    
    Attributes
    ----------
    name : str
        Имя клиента
    email : str
        Email клиента (валидируется)
    phone : str
        Номер телефона (валидируется)
    address : str
        Адрес доставки
    """
    
    # Регулярные выражения для валидации
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{8,14}$')  # E.164 формат (минимум 9 цифр после первой)
    
    def __init__(self, customer_id: int, name: str, email: str, 
                 phone: str, address: str = ""):
        """
        Инициализация клиента.
        
        Parameters
        ----------
        customer_id : int
            Уникальный идентификатор клиента
        name : str
            Имя клиента
        email : str
            Email клиента (проверяется валидность)
        phone : str
            Номер телефона (проверяется валидность)
        address : str, optional
            Адрес доставки
            
        Raises
        ------
        ValueError
            Если email или phone не соответствуют формату
        """
        super().__init__(customer_id)
        
        if not self.EMAIL_PATTERN.match(email):
            raise ValueError(f"Некорректный формат email: {email}")
        
        if not self.PHONE_PATTERN.match(phone):
            raise ValueError(f"Некорректный формат телефона: {phone}")
        
        self._name = name
        self._email = email
        self._phone = phone
        self._address = address
        self._orders_count = 0
    
    @property
    def name(self) -> str:
        """Получить имя клиента."""
        return self._name
    
    @property
    def email(self) -> str:
        """Получить email клиента."""
        return self._email
    
    @property
    def phone(self) -> str:
        """Получить номер телефона."""
        return self._phone
    
    @property
    def address(self) -> str:
        """Получить адрес доставки."""
        return self._address
    
    @property
    def orders_count(self) -> int:
        """Получить количество заказов клиента."""
        return self._orders_count
    
    def increment_orders_count(self) -> None:
        """Увеличить счётчик заказов на 1."""
        self._orders_count += 1
    
    def update_address(self, new_address: str) -> None:
        """
        Обновить адрес доставки.
        
        Parameters
        ----------
        new_address : str
            Новый адрес
        """
        self._address = new_address
    
    def __repr__(self) -> str:
        """Строковое представление клиента."""
        return f"Customer(id={self._id}, name='{self._name}', email='{self._email}', orders={self._orders_count})"


class Order(BaseEntity):
    """
    Класс для представления заказа.
    
    Демонстрирует полиморфизм через использование списка товаров.
    
    Attributes
    ----------
    customer_id : int
        ID клиента, сделавшего заказ
    items : List[tuple]
        Список кортежей (product, quantity)
    status : str
        Статус заказа (pending, processing, shipped, delivered, cancelled)
    """
    
    VALID_STATUSES = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    def __init__(self, order_id: int, customer_id: int, items: List[tuple] = None):
        """
        Инициализация заказа.
        
        Parameters
        ----------
        order_id : int
            Уникальный идентификатор заказа
        customer_id : int
            ID клиента
        items : List[tuple], optional
            Список кортежей (Product, quantity)
        """
        super().__init__(order_id)
        self._customer_id = customer_id
        self._items = items if items is not None else []
        self._status = 'pending'
        self._total_price = self._calculate_total()
    
    @property
    def customer_id(self) -> int:
        """Получить ID клиента."""
        return self._customer_id
    
    @property
    def items(self) -> List[tuple]:
        """Получить список товаров в заказе."""
        return self._items.copy()
    
    @property
    def status(self) -> str:
        """Получить статус заказа."""
        return self._status
    
    @property
    def total_price(self) -> float:
        """Получить общую стоимость заказа."""
        return self._total_price
    
    def add_item(self, product: Product, quantity: int) -> None:
        """
        Добавить товар в заказ.
        
        Parameters
        ----------
        product : Product
            Товар для добавления
        quantity : int
            Количество товара
            
        Raises
        ------
        ValueError
            Если количество <= 0
        """
        if quantity <= 0:
            raise ValueError("Количество товара должно быть больше 0")
        
        self._items.append((product, quantity))
        self._total_price = self._calculate_total()
    
    def remove_item(self, product_id: int) -> None:
        """
        Удалить товар из заказа.
        
        Parameters
        ----------
        product_id : int
            ID товара для удаления
        """
        self._items = [(p, q) for p, q in self._items if p.id != product_id]
        self._total_price = self._calculate_total()
    
    def set_status(self, new_status: str) -> None:
        """
        Изменить статус заказа.
        
        Parameters
        ----------
        new_status : str
            Новый статус (должен быть из VALID_STATUSES)
            
        Raises
        ------
        ValueError
            Если статус не валиден
        """
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Некорректный статус. Допустимые: {self.VALID_STATUSES}")
        self._status = new_status
    
    def _calculate_total(self) -> float:
        """
        Вычислить общую стоимость заказа.
        
        Returns
        -------
        float
            Сумма всех товаров в заказе
        """
        return sum(product.price * quantity for product, quantity in self._items)
    
    def get_items_count(self) -> int:
        """
        Получить общее количество товаров в заказе.
        
        Returns
        -------
        int
            Сумма количеств всех товаров
        """
        return sum(quantity for _, quantity in self._items)
    
    def __repr__(self) -> str:
        """Строковое представление заказа."""
        return f"Order(id={self._id}, customer_id={self._customer_id}, status='{self._status}', total={self._total_price})"


# Функции для сортировки (демонстрация лямбда-выражений и функциональных подходов)

def sort_orders_by_date(orders: List[Order], reverse: bool = False) -> List[Order]:
    """
    Отсортировать заказы по дате создания.
    
    Parameters
    ----------
    orders : List[Order]
        Список заказов
    reverse : bool, optional
        Если True, сортировка в обратном порядке
        
    Returns
    -------
    List[Order]
        Отсортированный список заказов
    """
    return sorted(orders, key=lambda order: order.created_at, reverse=reverse)


def sort_orders_by_price(orders: List[Order], reverse: bool = True) -> List[Order]:
    """
    Отсортировать заказы по стоимости.
    
    Parameters
    ----------
    orders : List[Order]
        Список заказов
    reverse : bool, optional
        Если True, сортировка по убыванию (по умолчанию)
        
    Returns
    -------
    List[Order]
        Отсортированный список заказов
    """
    return sorted(orders, key=lambda order: order.total_price, reverse=reverse)


def sort_customers_by_orders(customers: List[Customer], reverse: bool = True) -> List[Customer]:
    """
    Отсортировать клиентов по количеству заказов.
    
    Parameters
    ----------
    customers : List[Customer]
        Список клиентов
    reverse : bool, optional
        Если True, сортировка по убыванию (по умолчанию)
        
    Returns
    -------
    List[Customer]
        Отсортированный список клиентов
    """
    return sorted(customers, key=lambda customer: customer.orders_count, reverse=reverse)
