
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path

from models import Product, Customer, Order
from db import DatabaseManager


class DataAnalyzer:
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.output_dir = Path("data/charts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройка стиля графиков
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
    
    def get_sales_by_date(self) -> pd.DataFrame:
        orders = self.db.get_all_orders()
        
        if not orders:
            return pd.DataFrame()
        
        data = {
            'date': [order.created_at.date() for order in orders],
            'total': [order.total_price for order in orders],
            'items': [order.get_items_count() for order in orders]
        }
        
        df = pd.DataFrame(data)
        df = df.groupby('date').agg({'total': 'sum', 'items': 'sum'}).reset_index()
        df = df.sort_values('date')
        
        return df
    
    def get_top_customers(self, n: int = 5) -> pd.DataFrame:
        customers = self.db.get_all_customers()
        
        if not customers:
            return pd.DataFrame()
        
        data = {
            'name': [c.name for c in customers],
            'orders': [c.orders_count for c in customers],
            'email': [c.email for c in customers]
        }
        
        df = pd.DataFrame(data)
        df = df.sort_values('orders', ascending=False).head(n)
        
        return df
    
    def get_top_products(self, n: int = 5) -> pd.DataFrame:
        orders = self.db.get_all_orders()
        
        if not orders:
            return pd.DataFrame()
        
        product_sales = {}
        for order in orders:
            for product, quantity in order.items:
                if product.id not in product_sales:
                    product_sales[product.id] = {
                        'name': product.name,
                        'quantity': 0,
                        'revenue': 0
                    }
                product_sales[product.id]['quantity'] += quantity
                product_sales[product.id]['revenue'] += product.price * quantity
        
        data = {
            'name': [v['name'] for v in product_sales.values()],
            'quantity': [v['quantity'] for v in product_sales.values()],
            'revenue': [v['revenue'] for v in product_sales.values()]
        }
        
        df = pd.DataFrame(data)
        df = df.sort_values('quantity', ascending=False).head(n)
        
        return df
    
    def get_order_status_distribution(self) -> pd.DataFrame:
        orders = self.db.get_all_orders()
        
        if not orders:
            return pd.DataFrame()
        
        status_counts = {}
        for order in orders:
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        data = {
            'status': list(status_counts.keys()),
            'count': list(status_counts.values())
        }
        
        df = pd.DataFrame(data)
        
        return df
    
    def plot_sales_dynamics(self) -> str:
        df = self.get_sales_by_date()
        
        if df.empty:
            print("Нет данных для построения графика")
            return ""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # График суммы продаж
        ax1.plot(df['date'], df['total'], marker='o', linewidth=2, color='#2E86AB')
        ax1.fill_between(df['date'], df['total'], alpha=0.3, color='#2E86AB')
        ax1.set_title('Динамика суммы продаж по датам', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Дата')
        ax1.set_ylabel('Сумма (руб.)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # График количества товаров
        ax2.bar(df['date'], df['items'], color='#A23B72', alpha=0.7)
        ax2.set_title('Количество товаров в заказах по датам', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Дата')
        ax2.set_ylabel('Количество товаров')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        output_file = self.output_dir / "sales_dynamics.png"
        plt.savefig(output_file, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"✓ График сохранён: {output_file}")
        return str(output_file)
    
    def plot_top_customers(self, n: int = 5) -> str:
        df = self.get_top_customers(n)
        
        if df.empty:
            print("Нет данных для построения графика")
            return ""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.barh(df['name'], df['orders'], color='#F18F01')
        ax.set_title(f'Топ {n} клиентов по количеству заказов', fontsize=14, fontweight='bold')
        ax.set_xlabel('Количество заказов')
        ax.set_ylabel('Клиент')
        
        # Добавить значения на столбцы
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        output_file = self.output_dir / "top_customers.png"
        plt.savefig(output_file, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"✓ График сохранён: {output_file}")
        return str(output_file)
    
    def plot_top_products(self, n: int = 5) -> str:
        df = self.get_top_products(n)
        
        if df.empty:
            print("Нет данных для построения графика")
            return ""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # График по количеству
        bars1 = ax1.bar(df['name'], df['quantity'], color='#06A77D')
        ax1.set_title(f'Топ {n} товаров по количеству продаж', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Количество')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')
        
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        # График по выручке
        bars2 = ax2.bar(df['name'], df['revenue'], color='#D62828')
        ax2.set_title(f'Топ {n} товаров по выручке', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Выручка (руб.)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        output_file = self.output_dir / "top_products.png"
        plt.savefig(output_file, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"✓ График сохранён: {output_file}")
        return str(output_file)
    
    def plot_order_status_distribution(self) -> str:
        df = self.get_order_status_distribution()
        
        if df.empty:
            print("Нет данных для построения графика")
            return ""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        # Круговая диаграмма
        wedges, texts, autotexts = ax1.pie(df['count'], labels=df['status'], autopct='%1.1f%%',
                                            colors=colors[:len(df)], startangle=90)
        ax1.set_title('Распределение заказов по статусам', fontsize=12, fontweight='bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Столбчатая диаграмма
        bars = ax2.bar(df['status'], df['count'], color=colors[:len(df)])
        ax2.set_title('Количество заказов по статусам', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Количество заказов')
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        output_file = self.output_dir / "order_status_distribution.png"
        plt.savefig(output_file, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"✓ График сохранён: {output_file}")
        return str(output_file)
    
    def get_summary_statistics(self) -> Dict[str, any]:
        products = self.db.get_all_products()
        customers = self.db.get_all_customers()
        orders = self.db.get_all_orders()
        
        total_revenue = sum(order.total_price for order in orders)
        avg_order_value = total_revenue / len(orders) if orders else 0
        total_items = sum(order.get_items_count() for order in orders)
        
        return {
            'total_products': len(products),
            'total_customers': len(customers),
            'total_orders': len(orders),
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'total_items_sold': total_items,
            'avg_items_per_order': total_items / len(orders) if orders else 0
        }
    
    def print_summary_statistics(self) -> None:
        """Вывести сводную статистику в консоль."""
        stats = self.get_summary_statistics()
        
        print("\n" + "="*50)
        print("СВОДНАЯ СТАТИСТИКА")
        print("="*50)
        print(f"Всего товаров: {stats['total_products']}")
        print(f"Всего клиентов: {stats['total_customers']}")
        print(f"Всего заказов: {stats['total_orders']}")
        print(f"Общая выручка: {stats['total_revenue']:.2f} руб.")
        print(f"Средняя стоимость заказа: {stats['avg_order_value']:.2f} руб.")
        print(f"Всего товаров продано: {stats['total_items_sold']}")
        print(f"Среднее товаров на заказ: {stats['avg_items_per_order']:.2f}")
        print("="*50 + "\n")
