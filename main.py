"""
Модуль main.py - Точка входа в приложение.

Этот модуль запускает главное окно приложения и инициализирует все компоненты.
"""

import sys
import tkinter as tk
from pathlib import Path

# Добавить текущую директорию в путь поиска модулей
sys.path.insert(0, str(Path(__file__).parent))

from gui import OnlineStoreApp


def main():
    """
    Главная функция приложения.
    
    Создаёт главное окно Tkinter и запускает приложение.
    """
    try:
        root = tk.Tk()
        app = OnlineStoreApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
