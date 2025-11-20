
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
import threading
from PIL import Image, ImageTk

from models import Product, Customer, Order
from db import DatabaseManager
from analysis import DataAnalyzer


class OnlineStoreApp:
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Менеджер интернет-магазина")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Инициализация БД и анализатора
        self.db = DatabaseManager()
        self.analyzer = DataAnalyzer(self.db)
        
        # Переменные состояния
        self.current_tab = "products"
        self.selected_product_id = None
        self.selected_customer_id = None
        self.selected_order_id = None
        
        # Создание интерфейса
        self._create_menu()
        self._create_notebook()
        self._load_data()
    
    def _create_menu(self) -> None:
        """Создать меню приложения."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт в CSV", command=self._export_csv)
        file_menu.add_command(label="Экспорт в JSON", command=self._export_json)
        file_menu.add_command(label="Импорт из CSV", command=self._import_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Анализ"
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Анализ", menu=analysis_menu)
        analysis_menu.add_command(label="Динамика продаж", command=self._show_sales_dynamics)
        analysis_menu.add_command(label="Топ клиентов", command=self._show_top_customers)
        analysis_menu.add_command(label="Топ товаров", command=self._show_top_products)
        analysis_menu.add_command(label="Статусы заказов", command=self._show_order_status)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Статистика", command=self._show_statistics)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
    
    def _create_notebook(self) -> None:
        """Создать вкладки интерфейса."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка "Товары"
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Товары")
        self._create_products_tab()
        
        # Вкладка "Клиенты"
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text="Клиенты")
        self._create_customers_tab()
        
        # Вкладка "Заказы"
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Заказы")
        self._create_orders_tab()
    
    def _create_products_tab(self) -> None:
        """Создать вкладку управления товарами."""
        # Фрейм для формы добавления
        form_frame = ttk.LabelFrame(self.products_frame, text="Добавить товар", padding=10)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.product_name = ttk.Entry(form_frame, width=30)
        self.product_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Цена (руб.):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.product_price = ttk.Entry(form_frame, width=30)
        self.product_price.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.product_desc = ttk.Entry(form_frame, width=30)
        self.product_desc.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Количество:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.product_qty = ttk.Entry(form_frame, width=30)
        self.product_qty.grid(row=3, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Добавить", command=self._add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self._clear_product_form).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для таблицы
        table_frame = ttk.LabelFrame(self.products_frame, text="Список товаров", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица товаров
        self.products_tree = ttk.Treeview(table_frame, columns=('ID', 'Название', 'Цена', 'Описание', 'Кол-во'), 
                                          height=15, show='headings')
        self.products_tree.column('ID', width=30)
        self.products_tree.column('Название', width=150)
        self.products_tree.column('Цена', width=80)
        self.products_tree.column('Описание', width=200)
        self.products_tree.column('Кол-во', width=80)
        
        for col in ('ID', 'Название', 'Цена', 'Описание', 'Кол-во'):
            self.products_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscroll=scrollbar.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки действий
        action_frame = ttk.Frame(self.products_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(action_frame, text="Удалить", command=self._delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Обновить", command=self._load_products).pack(side=tk.LEFT, padx=5)
    
    def _create_customers_tab(self) -> None:
        """Создать вкладку управления клиентами."""
        # Фрейм для формы регистрации
        form_frame = ttk.LabelFrame(self.customers_frame, text="Зарегистрировать клиента", padding=10)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_name = ttk.Entry(form_frame, width=30)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_email = ttk.Entry(form_frame, width=30)
        self.customer_email.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_phone = ttk.Entry(form_frame, width=30)
        self.customer_phone.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Адрес:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_address = ttk.Entry(form_frame, width=30)
        self.customer_address.grid(row=3, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Зарегистрировать", command=self._add_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self._clear_customer_form).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для таблицы
        table_frame = ttk.LabelFrame(self.customers_frame, text="Список клиентов", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица клиентов
        self.customers_tree = ttk.Treeview(table_frame, columns=('ID', 'Имя', 'Email', 'Телефон', 'Адрес', 'Заказов'), 
                                           height=15, show='headings')
        self.customers_tree.column('ID', width=30)
        self.customers_tree.column('Имя', width=100)
        self.customers_tree.column('Email', width=150)
        self.customers_tree.column('Телефон', width=100)
        self.customers_tree.column('Адрес', width=200)
        self.customers_tree.column('Заказов', width=70)
        
        for col in ('ID', 'Имя', 'Email', 'Телефон', 'Адрес', 'Заказов'):
            self.customers_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscroll=scrollbar.set)
        
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки действий
        action_frame = ttk.Frame(self.customers_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(action_frame, text="Удалить", command=self._delete_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Обновить", command=self._load_customers).pack(side=tk.LEFT, padx=5)
    
    def _create_orders_tab(self) -> None:
        """Создать вкладку управления заказами."""
        # Фрейм для создания заказа
        form_frame = ttk.LabelFrame(self.orders_frame, text="Создать заказ", padding=10)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_customer = ttk.Combobox(form_frame, width=30, state='readonly')
        self.order_customer.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Товар:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_product = ttk.Combobox(form_frame, width=30, state='readonly')
        self.order_product.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Количество:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.order_quantity = ttk.Entry(form_frame, width=30)
        self.order_quantity.grid(row=2, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Создать заказ", command=self._create_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self._clear_order_form).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для таблицы
        table_frame = ttk.LabelFrame(self.orders_frame, text="Список заказов", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица заказов
        self.orders_tree = ttk.Treeview(table_frame, columns=('ID', 'Клиент', 'Статус', 'Сумма', 'Дата'), 
                                        height=15, show='headings')
        self.orders_tree.column('ID', width=30)
        self.orders_tree.column('Клиент', width=150)
        self.orders_tree.column('Статус', width=100)
        self.orders_tree.column('Сумма', width=100)
        self.orders_tree.column('Дата', width=150)
        
        for col in ('ID', 'Клиент', 'Статус', 'Сумма', 'Дата'):
            self.orders_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscroll=scrollbar.set)
        
        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки действий
        action_frame = ttk.Frame(self.orders_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(action_frame, text="Изменить статус", command=self._change_order_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Удалить", command=self._delete_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Обновить", command=self._load_orders).pack(side=tk.LEFT, padx=5)
    
    # ============ ТОВАРЫ ============
    
    def _add_product(self) -> None:
        """Добавить новый товар."""
        try:
            name = self.product_name.get().strip()
            price = float(self.product_price.get())
            description = self.product_desc.get().strip()
            quantity = int(self.product_qty.get())
            
            if not name:
                messagebox.showerror("Ошибка", "Введите название товара")
                return
            
            product = Product(0, name, price, description, quantity)
            self.db.add_product(product)
            
            messagebox.showinfo("Успех", "Товар добавлен успешно")
            self._clear_product_form()
            self._load_products()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
    
    def _delete_product(self) -> None:
        """Удалить выбранный товар."""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = int(item['values'][0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены?"):
            self.db.delete_product(product_id)
            messagebox.showinfo("Успех", "Товар удалён")
            self._load_products()
    
    def _clear_product_form(self) -> None:
        """Очистить форму добавления товара."""
        self.product_name.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        self.product_desc.delete(0, tk.END)
        self.product_qty.delete(0, tk.END)
    
    def _load_products(self) -> None:
        """Загрузить товары в таблицу."""
        self.products_tree.delete(*self.products_tree.get_children())
        for product in self.db.get_all_products():
            self.products_tree.insert('', tk.END, values=(
                product.id, product.name, f"{product.price:.2f}",
                product.description, product.quantity
            ))
        self._update_product_combobox()
    
    def _update_product_combobox(self) -> None:
        """Обновить список товаров в комбобоксе."""
        products = self.db.get_all_products()
        self.order_product['values'] = [f"{p.name} (ID: {p.id})" for p in products]
    
    # ============ КЛИЕНТЫ ============
    
    def _add_customer(self) -> None:
        """Добавить нового клиента."""
        try:
            name = self.customer_name.get().strip()
            email = self.customer_email.get().strip()
            phone = self.customer_phone.get().strip()
            address = self.customer_address.get().strip()
            
            if not name or not email or not phone:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
            
            customer = Customer(0, name, email, phone, address)
            self.db.add_customer(customer)
            
            messagebox.showinfo("Успех", "Клиент зарегистрирован успешно")
            self._clear_customer_form()
            self._load_customers()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
    
    def _delete_customer(self) -> None:
        """Удалить выбранного клиента."""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return
        
        item = self.customers_tree.item(selection[0])
        customer_id = int(item['values'][0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены?"):
            self.db.delete_customer(customer_id)
            messagebox.showinfo("Успех", "Клиент удалён")
            self._load_customers()
    
    def _clear_customer_form(self) -> None:
        """Очистить форму регистрации клиента."""
        self.customer_name.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        self.customer_address.delete(0, tk.END)
    
    def _load_customers(self) -> None:
        """Загрузить клиентов в таблицу."""
        self.customers_tree.delete(*self.customers_tree.get_children())
        for customer in self.db.get_all_customers():
            self.customers_tree.insert('', tk.END, values=(
                customer.id, customer.name, customer.email,
                customer.phone, customer.address, customer.orders_count
            ))
        self._update_customer_combobox()
    
    def _update_customer_combobox(self) -> None:
        """Обновить список клиентов в комбобоксе."""
        customers = self.db.get_all_customers()
        self.order_customer['values'] = [f"{c.name} (ID: {c.id})" for c in customers]
    
    # ============ ЗАКАЗЫ ============
    
    def _create_order(self) -> None:
        """Создать новый заказ."""
        try:
            customer_str = self.order_customer.get()
            product_str = self.order_product.get()
            quantity_str = self.order_quantity.get()
            
            if not customer_str or not product_str or not quantity_str:
                messagebox.showerror("Ошибка", "Выберите клиента, товар и введите количество")
                return
            
            # Извлечь ID из строк
            customer_id = int(customer_str.split("ID: ")[1].rstrip(")"))
            product_id = int(product_str.split("ID: ")[1].rstrip(")"))
            quantity = int(quantity_str)
            
            order = Order(0, customer_id)
            product = self.db.get_product(product_id)
            
            if product:
                order.add_item(product, quantity)
                self.db.add_order(order)
                
                messagebox.showinfo("Успех", "Заказ создан успешно")
                self._clear_order_form()
                self._load_orders()
        except (ValueError, IndexError) as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
    
    def _change_order_status(self) -> None:
        """Изменить статус заказа."""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = int(item['values'][0])
        
        # Создать окно для выбора статуса
        status_window = tk.Toplevel(self.root)
        status_window.title("Изменить статус")
        status_window.geometry("300x150")
        
        ttk.Label(status_window, text="Выберите новый статус:").pack(pady=10)
        
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(status_window, textvariable=status_var, 
                                    values=['pending', 'processing', 'shipped', 'delivered', 'cancelled'],
                                    state='readonly', width=30)
        status_combo.pack(pady=10)
        
        def save_status():
            if status_var.get():
                self.db.update_order_status(order_id, status_var.get())
                messagebox.showinfo("Успех", "Статус обновлён")
                self._load_orders()
                status_window.destroy()
        
        ttk.Button(status_window, text="Сохранить", command=save_status).pack(pady=10)
    
    def _delete_order(self) -> None:
        """Удалить выбранный заказ."""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = int(item['values'][0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены?"):
            self.db.delete_order(order_id)
            messagebox.showinfo("Успех", "Заказ удалён")
            self._load_orders()
    
    def _clear_order_form(self) -> None:
        """Очистить форму создания заказа."""
        self.order_customer.set('')
        self.order_product.set('')
        self.order_quantity.delete(0, tk.END)
    
    def _load_orders(self) -> None:
        """Загрузить заказы в таблицу."""
        self.orders_tree.delete(*self.orders_tree.get_children())
        for order in self.db.get_all_orders():
            customer = self.db.get_customer(order.customer_id)
            customer_name = customer.name if customer else "Неизвестно"
            
            self.orders_tree.insert('', tk.END, values=(
                order.id, customer_name, order.status,
                f"{order.total_price:.2f}", order.created_at.strftime("%Y-%m-%d %H:%M")
            ))
    
    # ============ АНАЛИЗ ============
    
    def _show_sales_dynamics(self) -> None:
        """Показать график динамики продаж."""
        self.analyzer.plot_sales_dynamics()
        messagebox.showinfo("Успех", "График сохранён в data/charts/sales_dynamics.png")
    
    def _show_top_customers(self) -> None:
        """Показать график топовых клиентов."""
        self.analyzer.plot_top_customers(5)
        messagebox.showinfo("Успех", "График сохранён в data/charts/top_customers.png")
    
    def _show_top_products(self) -> None:
        """Показать график топовых товаров."""
        self.analyzer.plot_top_products(5)
        messagebox.showinfo("Успех", "График сохранён в data/charts/top_products.png")
    
    def _show_order_status(self) -> None:
        """Показать график распределения статусов."""
        self.analyzer.plot_order_status_distribution()
        messagebox.showinfo("Успех", "График сохранён в data/charts/order_status_distribution.png")
    
    def _show_statistics(self) -> None:
        """Показать статистику."""
        stats = self.analyzer.get_summary_statistics()
        
        message = f"""
СВОДНАЯ СТАТИСТИКА
{'='*40}
Всего товаров: {stats['total_products']}
Всего клиентов: {stats['total_customers']}
Всего заказов: {stats['total_orders']}
Общая выручка: {stats['total_revenue']:.2f} руб.
Средняя стоимость заказа: {stats['avg_order_value']:.2f} руб.
Всего товаров продано: {stats['total_items_sold']}
Среднее товаров на заказ: {stats['avg_items_per_order']:.2f}
        """
        
        messagebox.showinfo("Статистика", message)
    
    # ============ ИМПОРТ/ЭКСПОРТ ============
    
    def _export_csv(self) -> None:
        """Экспортировать данные в CSV."""
        self.db.export_to_csv()
        messagebox.showinfo("Успех", "Данные экспортированы в data/")
    
    def _export_json(self) -> None:
        """Экспортировать данные в JSON."""
        self.db.export_to_json()
        messagebox.showinfo("Успех", "Данные экспортированы в data/")
    
    def _import_csv(self) -> None:
        """Импортировать данные из CSV."""
        dir_path = filedialog.askdirectory(title="Выберите директорию с CSV файлами")
        if dir_path:
            self.db.import_from_csv(dir_path)
            messagebox.showinfo("Успех", "Данные импортированы")
            self._load_data()
    
    # ============ ПОМОЩЬ ============
    
    def _show_about(self) -> None:
        """Показать информацию о программе."""
        messagebox.showinfo("О программе", 
            "Менеджер интернет-магазина v1.0\n\n"
            "Приложение для управления товарами, клиентами и заказами.\n\n"
            "Разработано как учебный проект."
        )
    
    # ============ ЗАГРУЗКА ДАННЫХ ============
    
    def _load_data(self) -> None:
        """Загрузить все данные при запуске."""
        self._load_products()
        self._load_customers()
        self._load_orders()


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = OnlineStoreApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
