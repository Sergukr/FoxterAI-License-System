"""
Компонент панели статистики с премиум дизайном
Карточки с изумрудными и золотыми акцентами согласно дизайн-гайду
"""

import customtkinter as ctk
from typing import Dict, Any
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from themes.dark_theme import DarkTheme


class StatCard(ctk.CTkFrame):
    """Премиум карточка статистики с 3D эффектами и анимацией"""
    
    def __init__(self, parent, title: str, value: str = "0", 
                 icon: str = "📊", card_type: str = "default"):
        """
        Инициализация карточки
        
        Args:
            parent: Родительский виджет
            title: Заголовок карточки
            value: Значение
            icon: Иконка (3D эмодзи согласно дизайн-гайду)
            card_type: Тип карточки для стилизации
        """
        # Получаем стили для карточки
        card_styles = self._get_card_styles(card_type)
        super().__init__(parent, **card_styles)
        
        self.title = title
        self.value = value
        self.icon = icon
        self.card_type = card_type
        self.is_animating = False
        
        self._setup_ui()
        
        # Запуск pulse анимации для иконки (каждые 4-5 секунд)
        self.after(4500, self._start_icon_pulse)
    
    def _get_card_styles(self, card_type: str) -> dict:
        """Получить стили для карточки согласно дизайн-гайду"""
        base_style = {
            "fg_color": DarkTheme.BG_CARD,
            "corner_radius": DarkTheme.RADIUS_LARGE,
            "border_width": 2,
            "height": 100
        }
        
        # Специальные стили и рамки для разных типов карточек
        if card_type == "total":
            base_style["border_color"] = DarkTheme.CHAMPAGNE_GOLD  # Золотая рамка для премиума
        elif card_type == "active":
            base_style["border_color"] = DarkTheme.JADE_GREEN      # Зеленая для активных
        elif card_type == "expired":
            base_style["border_color"] = DarkTheme.COPPER_BRONZE   # Бронзовая для истекших
        elif card_type == "blocked":
            base_style["border_color"] = "#D32F2F"                 # Красная для заблокированных
        elif card_type == "inactive":
            base_style["border_color"] = DarkTheme.WARM_GRAY       # Серая для неактивных
        elif card_type == "balance":
            base_style["border_color"] = DarkTheme.CHAMPAGNE_GOLD  # Золотая для баланса
        else:
            base_style["border_color"] = DarkTheme.BORDER
        
        return base_style
    
    def _setup_ui(self):
        """Настройка UI карточки согласно дизайн-гайду"""
        # Главный контейнер
        main_container = ctk.CTkFrame(self, fg_color='transparent')
        main_container.pack(fill='both', expand=True, padx=10, pady=8)
        
        # Левая часть - иконка с эффектом свечения
        icon_container = ctk.CTkFrame(
            main_container,
            fg_color=self._get_icon_bg_color(),
            width=50,
            height=50,
            corner_radius=10
        )
        icon_container.pack(side='left', padx=(5, 15))
        icon_container.pack_propagate(False)
        
        # 3D иконка (согласно дизайн-гайду)
        self.icon_label = ctk.CTkLabel(
            icon_container,
            text=self.icon,
            font=("Segoe UI Emoji", 24)
        )
        self.icon_label.pack(expand=True)
        
        # Правая часть - текст и значение
        text_container = ctk.CTkFrame(main_container, fg_color='transparent')
        text_container.pack(side='left', fill='both', expand=True)
        
        # Заголовок карточки (размер 18-20px согласно гайду)
        self.title_label = ctk.CTkLabel(
            text_container,
            text=self.title,
            font=("Inter", 12),  # Немного увеличим для соответствия гайду
            text_color=DarkTheme.WARM_GRAY,
            anchor='w'
        )
        self.title_label.pack(fill='x', pady=(5, 2))
        
        # Значение (большие цифры 24-28px согласно гайду)
        self.value_label = ctk.CTkLabel(
            text_container,
            text=self.value,
            font=("Inter", 26, "bold"),  # Увеличено до 26px для соответствия гайду
            text_color=self._get_value_color(),
            anchor='w'
        )
        self.value_label.pack(fill='x')
        
        # Hover эффекты для всей карточки
        for widget in [self, main_container, icon_container, text_container]:
            widget.bind("<Enter>", self._on_hover_enter)
            widget.bind("<Leave>", self._on_hover_leave)
    
    def _get_icon_bg_color(self) -> str:
        """Получить цвет фона для иконки"""
        colors = {
            "total": DarkTheme.DEEP_EMERALD,
            "active": DarkTheme.JADE_GREEN,
            "expired": DarkTheme.COPPER_BRONZE,
            "blocked": "#3A1F1F",  # Темно-красный фон
            "inactive": "#2A2A2A",  # Темно-серый фон
            "balance": DarkTheme.CHAMPAGNE_GOLD
        }
        return colors.get(self.card_type, DarkTheme.BG_TERTIARY)
    
    def _get_value_color(self) -> str:
        """Получить цвет для значения согласно дизайн-гайду"""
        colors = {
            "total": DarkTheme.PURE_WHITE,
            "active": DarkTheme.JADE_GREEN,       # Зеленый для активных
            "expired": DarkTheme.COPPER_BRONZE,   # Бронзовый для истекших
            "blocked": "#FF5252",                  # Красный для заблокированных
            "inactive": DarkTheme.WARM_GRAY,      # Серый для неактивных
            "balance": DarkTheme.CHAMPAGNE_GOLD   # Золотой для денег
        }
        return colors.get(self.card_type, DarkTheme.TEXT_PRIMARY)
    
    def update_value(self, new_value: str):
        """Обновление значения с count-up анимацией (согласно гайду)"""
        self.value = new_value
        
        # Анимация появления нового значения
        self._animate_value_change(new_value)
    
    def _animate_value_change(self, new_value: str):
        """Count-up анимация для цифр"""
        # Проверяем, является ли значение числом
        try:
            # Убираем символы валюты и K для анимации
            clean_value = new_value.replace('$', '').replace('K', '').replace(',', '')
            target_num = float(clean_value)
            is_currency = '$' in new_value
            is_thousands = 'K' in new_value
            
            # Анимируем от 0 до целевого значения
            self._count_up_animation(0, target_num, is_currency, is_thousands)
        except:
            # Если не число, просто обновляем
            self.value_label.configure(text=new_value)
    
    def _count_up_animation(self, current: float, target: float, 
                           is_currency: bool, is_thousands: bool, step: int = 0):
        """Анимация подсчета от текущего к целевому"""
        if step > 20:  # Максимум 20 шагов анимации
            # Финальное значение
            if is_currency:
                if is_thousands:
                    final_text = f"${target:.1f}K"
                else:
                    final_text = f"${target:.0f}"
            else:
                final_text = str(int(target))
            
            self.value_label.configure(text=final_text)
            return
        
        # Интерполяция значения
        progress = step / 20
        interpolated = current + (target - current) * progress
        
        # Форматирование текущего значения
        if is_currency:
            if is_thousands:
                display_text = f"${interpolated:.1f}K"
            else:
                display_text = f"${interpolated:.0f}"
        else:
            display_text = str(int(interpolated))
        
        self.value_label.configure(text=display_text)
        
        # Следующий шаг через 30мс
        self.after(30, lambda: self._count_up_animation(
            current, target, is_currency, is_thousands, step + 1
        ))
    
    def _on_hover_enter(self, event):
        """Hover эффект - подъем карточки (scale 1.02 согласно гайду)"""
        # Изменяем цвет границы для эффекта свечения
        hover_colors = {
            "total": DarkTheme.CHAMPAGNE_GOLD,
            "active": DarkTheme.JADE_GREEN,
            "expired": DarkTheme.COPPER_BRONZE,
            "blocked": "#FF5252",
            "inactive": DarkTheme.WARM_GRAY,
            "balance": DarkTheme.CHAMPAGNE_GOLD
        }
        
        new_border = hover_colors.get(self.card_type, DarkTheme.JADE_GREEN)
        # Увеличиваем ширину границы для эффекта "подъема"
        self.configure(border_color=new_border, border_width=3)
    
    def _on_hover_leave(self, event):
        """Убираем hover эффект"""
        self.configure(border_width=2)
    
    def _start_icon_pulse(self):
        """Запуск pulse анимации иконки (каждые 4-5 секунд согласно гайду)"""
        if not self.is_animating:
            self.is_animating = True
            self._pulse_icon()
    
    def _pulse_icon(self):
        """Pulse анимация иконки"""
        if not self.is_animating:
            return
        
        # Увеличиваем размер иконки
        self.icon_label.configure(font=("Segoe UI Emoji", 26))
        self.after(200, lambda: self.icon_label.configure(font=("Segoe UI Emoji", 24)))
        
        # Повторяем через 4.5 секунды
        self.after(4500, self._pulse_icon)


class StatsPanel(ctk.CTkFrame):
    """Панель статистики с премиум карточками"""
    
    def __init__(self, parent, stats: Dict[str, Any] = None):
        """
        Инициализация панели статистики
        
        Args:
            parent: Родительский виджет
            stats: Начальная статистика
        """
        super().__init__(
            parent,
            fg_color=DarkTheme.BG_PRIMARY,
            corner_radius=0,
            height=120
        )
        
        self.stats = stats or self._get_default_stats()
        self.cards = {}
        
        self._setup_ui()
        self.update_stats(self.stats)
    
    def _get_default_stats(self) -> Dict[str, Any]:
        """Получить статистику по умолчанию"""
        return {
            'total': 0,
            'active': 0,
            'expired': 0,
            'blocked': 0,
            'inactive': 0,
            'balance': 0.0
        }
    
    def _setup_ui(self):
        """Настройка интерфейса с премиум карточками"""
        # Контейнер для карточек
        cards_container = ctk.CTkFrame(self, fg_color='transparent')
        cards_container.pack(fill='both', expand=True)
        
        # Конфигурация сетки - 6 колонок для карточек
        for i in range(6):
            cards_container.grid_columnconfigure(i, weight=1, minsize=180)
        
        # Создаем премиум карточки согласно дизайн-гайду
        # Используем 3D иконки из гайда
        card_configs = [
            {
                'key': 'balance',
                'title': '📊 Баланс',
                'icon': '💰',  # Мешок с золотыми монетами
                'card_type': 'balance',
                'column': 0
            },
            {
                'key': 'total',
                'title': '🎟 Всего лицензий',
                'icon': '💎',  # Бриллиант-премиум
                'card_type': 'total',
                'column': 1
            },
            {
                'key': 'active',
                'title': '✅ Активные',
                'icon': '⭐',  # Звезда
                'card_type': 'active',
                'column': 2
            },
            {
                'key': 'expired',
                'title': '🕒 Истекающие',
                'icon': '⏳',  # Песочные часы
                'card_type': 'expired',
                'column': 3
            },
            {
                'key': 'blocked',
                'title': '🔒 Заблокированные',
                'icon': '🔒',  # Массивный замок
                'card_type': 'blocked',
                'column': 4
            },
            {
                'key': 'inactive',
                'title': '🌙 Неактивированные',
                'icon': '🌙',  # Луна со свечением
                'card_type': 'inactive',
                'column': 5
            }
        ]
        
        # Создаем карточки
        for config in card_configs:
            card = StatCard(
                cards_container,
                title=config['title'],
                value="0",
                icon=config['icon'],
                card_type=config['card_type']
            )
            card.grid(row=0, column=config['column'], padx=7, pady=10, sticky='nsew')
            self.cards[config['key']] = card
    
    def update_stats(self, stats: Dict[str, Any]):
        """Обновление статистики с анимацией"""
        self.stats = stats
        
        # Обновляем баланс (с золотым текстом согласно гайду)
        if 'balance' in stats and 'balance' in self.cards:
            balance = stats['balance']
            if balance >= 1000:
                balance_str = f"${balance/1000:.1f}K"
            else:
                balance_str = f"${balance:.0f}"
            self.cards['balance'].update_value(balance_str)
        
        # Обновляем остальные карточки
        if 'total' in stats and 'total' in self.cards:
            self.cards['total'].update_value(str(stats['total']))
        
        if 'active' in stats and 'active' in self.cards:
            self.cards['active'].update_value(str(stats['active']))
        
        if 'expired' in stats and 'expired' in self.cards:
            self.cards['expired'].update_value(str(stats['expired']))
        
        if 'blocked' in stats and 'blocked' in self.cards:
            self.cards['blocked'].update_value(str(stats['blocked']))
        
        # Для "не активированных" используем поле 'created' или 'inactive'
        inactive_count = stats.get('inactive', stats.get('created', 0))
        if 'inactive' in self.cards:
            self.cards['inactive'].update_value(str(inactive_count))
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить текущую статистику"""
        return self.stats
    
    def reset_stats(self):
        """Сбросить статистику на значения по умолчанию"""
        self.update_stats(self._get_default_stats())
    
    def highlight_card(self, card_key: str):
        """
        Подсветить конкретную карточку
        
        Args:
            card_key: Ключ карточки для подсветки
        """
        if card_key in self.cards:
            card = self.cards[card_key]
            # Временная подсветка
            original_border = card.cget("border_width")
            card.configure(border_width=4)
            card.after(1000, lambda: card.configure(border_width=original_border))