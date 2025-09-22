"""
Премиум тема оформления FoxterAI License Manager v2.2
Современный дизайн с изумрудными и золотыми акцентами
ПОЛНЫЙ ФАЙЛ ДЛЯ ЗАМЕНЫ: FoxterAI_Desktop/themes/dark_theme.py
"""

class DarkTheme:
    """Премиум темная тема с изумрудными акцентами"""
    
    # ===== ОСНОВНЫЕ ЦВЕТА (из дизайн-гайда) =====
    
    # Primary (основные зелёные тона)
    DEEP_EMERALD = "#1B5E20"      # Главный акцент, логотип, кнопки
    JADE_GREEN = "#2E7D32"         # Активные элементы, статусы, подсветка
    SOFT_MINT = "#A5D6A7"          # Фоновые элементы, заливки в таблицах
    
    # Secondary (акценты)
    CHAMPAGNE_GOLD = "#D4AF37"    # Иконки, баланс, премиум-обводки
    COPPER_BRONZE = "#B87333"      # Вторичные акценты, предупреждения
    
    # Neutral / Background
    CHARCOAL_BLACK = "#121212"    # Основной фон
    GRAPHITE_GRAY = "#2C2C2C"     # Карточки, панели
    STONE_GRAY = "#ECEFF1"        # Светлая тема / вспомогательные зоны
    
    # Text
    PURE_WHITE = "#FFFFFF"        # Заголовки, главный текст
    WARM_GRAY = "#B0BEC5"         # Вторичный текст
    SOFT_BEIGE = "#F5F5DC"        # Подписи на зелёном фоне
    
    # ===== NEON ЦВЕТА (для совместимости) =====
    NEON_GREEN = "#39FF14"        # Яркий неоновый зеленый
    NEON_BLUE = "#00D4FF"         # Неоновый синий
    NEON_PURPLE = "#BC13FE"       # Неоновый фиолетовый
    NEON_PINK = "#FF10F0"         # Неоновый розовый
    NEON_YELLOW = "#FFFF00"       # Неоновый желтый
    NEON_ORANGE = "#FF9500"       # Неоновый оранжевый
    NEON_RED = "#FF073A"          # Неоновый красный
    
    # Приглушенные версии неоновых цветов
    NEON_GREEN_DIM = "#2E7D32"    # Приглушенный зеленый (JADE_GREEN)
    NEON_BLUE_DIM = "#0080B0"     # Приглушенный синий
    NEON_PURPLE_DIM = "#7B0F8E"   # Приглушенный фиолетовый
    NEON_PINK_DIM = "#B00B90"     # Приглушенный розовый
    
    # ===== АЛИАСЫ ДЛЯ КОМПОНЕНТОВ =====
    
    # Фоновые цвета
    BG_PRIMARY = CHARCOAL_BLACK       # Основной фон приложения
    BG_SECONDARY = GRAPHITE_GRAY      # Фон карточек и панелей
    BG_TERTIARY = "#1F1F1F"          # Третичный фон
    BG_HOVER = "#3A3A3A"              # При наведении
    BG_SELECTED = "#2E7D32"           # Выделенный элемент (JADE_GREEN)
    BG_CARD = GRAPHITE_GRAY           # Фон карточек
    BG_INPUT = "#1F1F1F"              # Фон полей ввода
    BG_MODAL = "#1A1A1A"              # Фон модальных окон
    BG_TOOLTIP = "#333333"            # Фон подсказок
    BG_NOTIFICATION = "#2A2A2A"       # Фон уведомлений
    
    # Цвета текста
    TEXT_PRIMARY = PURE_WHITE         # Основной текст
    TEXT_SECONDARY = WARM_GRAY        # Вторичный текст
    TEXT_DISABLED = "#616161"         # Отключенный текст
    TEXT_ON_PRIMARY = SOFT_BEIGE      # Текст на зеленом фоне
    TEXT_HINT = "#757575"             # Подсказки
    TEXT_LINK = "#64B5F6"             # Ссылки
    TEXT_ERROR = "#EF5350"            # Текст ошибки
    TEXT_WARNING = "#FFA726"          # Текст предупреждения
    TEXT_SUCCESS = "#66BB6A"          # Текст успеха
    
    # Цвета границ
    BORDER_PRIMARY = "#404040"        # Основные границы
    BORDER_SECONDARY = "#2A2A2A"      # Вторичные границы
    BORDER_ACCENT = JADE_GREEN        # Акцентные границы
    BORDER_ERROR = "#EF5350"          # Границы при ошибке
    BORDER_FOCUS = JADE_GREEN         # Границы при фокусе
    BORDER_DISABLED = "#333333"       # Границы отключенных элементов
    
    # Цвета кнопок
    BUTTON_PRIMARY = DEEP_EMERALD     # Основная кнопка
    BUTTON_PRIMARY_HOVER = JADE_GREEN # Основная кнопка при наведении
    BUTTON_SECONDARY = "#424242"      # Вторичная кнопка
    BUTTON_SECONDARY_HOVER = "#525252" # Вторичная кнопка при наведении
    BUTTON_DANGER = "#C62828"         # Опасная кнопка
    BUTTON_DANGER_HOVER = "#D32F2F"   # Опасная кнопка при наведении
    BUTTON_SUCCESS = "#388E3C"        # Кнопка успеха
    BUTTON_SUCCESS_HOVER = "#43A047"  # Кнопка успеха при наведении
    BUTTON_WARNING = "#F57C00"        # Кнопка предупреждения
    BUTTON_WARNING_HOVER = "#FF6F00"  # Кнопка предупреждения при наведении
    BUTTON_DISABLED = "#333333"       # Отключенная кнопка
    BUTTON_TEXT_PRIMARY = PURE_WHITE  # Текст на основной кнопке
    BUTTON_TEXT_SECONDARY = WARM_GRAY # Текст на вторичной кнопке
    
    # Цвета статусов
    STATUS_ACTIVE = "#4CAF50"         # Активный (зеленый)
    STATUS_EXPIRED = "#F44336"        # Истекший (красный)
    STATUS_BLOCKED = "#FF5722"        # Заблокированный (оранжево-красный)
    STATUS_PENDING = "#FF9800"        # Ожидающий/Не активирован (оранжевый)
    STATUS_WARNING = "#FFC107"        # Предупреждение (желтый)
    STATUS_INFO = "#2196F3"           # Информация (синий)
    STATUS_SUCCESS = "#4CAF50"        # Успех (зеленый)
    STATUS_ERROR = "#F44336"          # Ошибка (красный)
    STATUS_CREATED = "#FF9800"        # Создан (оранжевый)
    STATUS_PROCESSING = "#03A9F4"     # В обработке (голубой)
    STATUS_UNKNOWN = "#9E9E9E"        # Неизвестный (серый)
    
    # Цвета индикаторов
    INDICATOR_ONLINE = "#4CAF50"      # Онлайн
    INDICATOR_OFFLINE = "#9E9E9E"     # Офлайн
    INDICATOR_BUSY = "#FF9800"        # Занят
    INDICATOR_AWAY = "#FFC107"        # Отошел
    INDICATOR_ERROR = "#F44336"       # Ошибка
    
    # Цвета графиков
    CHART_PRIMARY = JADE_GREEN        # Основной цвет графика
    CHART_SECONDARY = CHAMPAGNE_GOLD  # Вторичный цвет графика
    CHART_TERTIARY = "#64B5F6"       # Третичный цвет графика
    CHART_SUCCESS = "#66BB6A"        # Успех на графике
    CHART_WARNING = "#FFA726"        # Предупреждение на графике
    CHART_ERROR = "#EF5350"          # Ошибка на графике
    CHART_GRID = "#333333"           # Сетка графика
    CHART_AXIS = "#666666"           # Оси графика
    
    # Цвета таблиц
    TABLE_HEADER_BG = "#1F1F1F"      # Фон заголовка таблицы
    TABLE_HEADER_TEXT = CHAMPAGNE_GOLD # Текст заголовка таблицы
    TABLE_ROW_BG = "#2A2A2A"         # Фон строки таблицы
    TABLE_ROW_ALT_BG = "#262626"     # Фон четной строки таблицы
    TABLE_ROW_HOVER = "#333333"      # Фон строки при наведении
    TABLE_ROW_SELECTED = JADE_GREEN  # Фон выделенной строки
    TABLE_BORDER = "#404040"         # Границы таблицы
    
    # Цвета форм
    INPUT_BG = "#1F1F1F"             # Фон поля ввода
    INPUT_BORDER = "#404040"         # Граница поля ввода
    INPUT_BORDER_FOCUS = JADE_GREEN  # Граница при фокусе
    INPUT_TEXT = PURE_WHITE          # Текст в поле ввода
    INPUT_PLACEHOLDER = "#757575"    # Placeholder текст
    INPUT_ERROR_BG = "#2C1A1A"      # Фон при ошибке
    INPUT_ERROR_BORDER = "#EF5350"  # Граница при ошибке
    
    # Цвета меню
    MENU_BG = "#1F1F1F"              # Фон меню
    MENU_ITEM_BG = "transparent"     # Фон элемента меню
    MENU_ITEM_HOVER = "#333333"      # Фон элемента при наведении
    MENU_ITEM_SELECTED = JADE_GREEN  # Фон выделенного элемента
    MENU_TEXT = PURE_WHITE           # Текст меню
    MENU_TEXT_DISABLED = "#616161"   # Отключенный текст меню
    MENU_SEPARATOR = "#404040"       # Разделитель меню
    
    # Цвета скроллбара
    SCROLLBAR_BG = "#1F1F1F"         # Фон скроллбара
    SCROLLBAR_THUMB = "#424242"      # Ползунок скроллбара
    SCROLLBAR_THUMB_HOVER = "#525252" # Ползунок при наведении
    SCROLLBAR_THUMB_ACTIVE = JADE_GREEN # Активный ползунок
    
    # Цвета тултипов
    TOOLTIP_BG = "#333333"            # Фон тултипа
    TOOLTIP_TEXT = PURE_WHITE         # Текст тултипа
    TOOLTIP_BORDER = "#404040"        # Граница тултипа
    
    # Цвета уведомлений
    NOTIFICATION_SUCCESS_BG = "#1B5E20"  # Фон успешного уведомления
    NOTIFICATION_ERROR_BG = "#B71C1C"    # Фон уведомления об ошибке
    NOTIFICATION_WARNING_BG = "#E65100"  # Фон предупреждения
    NOTIFICATION_INFO_BG = "#01579B"     # Фон информационного уведомления
    NOTIFICATION_TEXT = PURE_WHITE       # Текст уведомления
    
    # Цвета прогресс-бара
    PROGRESS_BG = "#1F1F1F"          # Фон прогресс-бара
    PROGRESS_FILL = JADE_GREEN       # Заполнение прогресс-бара
    PROGRESS_TEXT = PURE_WHITE       # Текст прогресс-бара
    
    # Цвета табов
    TAB_BG = "#1F1F1F"               # Фон таба
    TAB_ACTIVE_BG = JADE_GREEN       # Фон активного таба
    TAB_HOVER_BG = "#333333"         # Фон таба при наведении
    TAB_TEXT = WARM_GRAY             # Текст таба
    TAB_ACTIVE_TEXT = PURE_WHITE     # Текст активного таба
    
    # Цвета модальных окон
    MODAL_BG = "#1A1A1A"             # Фон модального окна
    MODAL_OVERLAY = "rgba(0,0,0,0.7)" # Затемнение под модалкой
    MODAL_BORDER = "#404040"         # Граница модального окна
    MODAL_HEADER_BG = "#242424"      # Фон заголовка модалки
    MODAL_FOOTER_BG = "#242424"      # Фон футера модалки
    
    # Градиенты (для CSS)
    GRADIENT_PRIMARY = "linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%)"
    GRADIENT_GOLD = "linear-gradient(135deg, #D4AF37 0%, #B87333 100%)"
    GRADIENT_DARK = "linear-gradient(135deg, #121212 0%, #2C2C2C 100%)"
    GRADIENT_SUCCESS = "linear-gradient(135deg, #388E3C 0%, #4CAF50 100%)"
    GRADIENT_ERROR = "linear-gradient(135deg, #C62828 0%, #F44336 100%)"
    GRADIENT_WARNING = "linear-gradient(135deg, #F57C00 0%, #FFB74D 100%)"
    GRADIENT_INFO = "linear-gradient(135deg, #0288D1 0%, #29B6F6 100%)"
    
    # Размеры
    RADIUS_SMALL = 4               # Маленький радиус
    RADIUS_NORMAL = 8              # Обычный радиус
    RADIUS_LARGE = 12              # Большой радиус
    RADIUS_EXTRA_LARGE = 16        # Очень большой радиус
    RADIUS_ROUND = 999             # Круглый
    
    # Отступы
    PADDING_TINY = 4               # Очень маленький отступ
    PADDING_SMALL = 8              # Маленький отступ
    PADDING_NORMAL = 12            # Обычный отступ
    PADDING_MEDIUM = 16            # Средний отступ
    PADDING_LARGE = 20             # Большой отступ
    PADDING_EXTRA_LARGE = 24       # Очень большой отступ
    
    # Тени
    SHADOW_SMALL = "0 2px 4px rgba(0,0,0,0.2)"
    SHADOW_NORMAL = "0 4px 8px rgba(0,0,0,0.3)"
    SHADOW_LARGE = "0 8px 16px rgba(0,0,0,0.4)"
    SHADOW_EXTRA_LARGE = "0 16px 32px rgba(0,0,0,0.5)"
    SHADOW_GLOW_GREEN = "0 0 20px rgba(46,125,50,0.4)"
    SHADOW_GLOW_GOLD = "0 0 20px rgba(212,175,55,0.4)"
    SHADOW_GLOW_RED = "0 0 20px rgba(244,67,54,0.4)"
    SHADOW_INSET = "inset 0 2px 4px rgba(0,0,0,0.2)"
    
    # Шрифты
    FONT_FAMILY = "Inter"
    FONT_FAMILY_MONO = "JetBrains Mono"
    FONT_FAMILY_HEADING = "Montserrat"
    FONT_SIZE_TINY = 10
    FONT_SIZE_SMALL = 11
    FONT_SIZE_NORMAL = 12
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_EXTRA_LARGE = 18
    FONT_SIZE_TITLE = 20
    FONT_SIZE_HEADING = 24
    FONT_SIZE_DISPLAY = 32
    
    # Веса шрифтов
    FONT_WEIGHT_LIGHT = 300
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700
    FONT_WEIGHT_EXTRABOLD = 800
    
    # Высота строки
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.8
    LINE_HEIGHT_LOOSE = 2.0
    
    # Анимации (длительность в миллисекундах)
    ANIMATION_INSTANT = 0
    ANIMATION_FAST = 150
    ANIMATION_NORMAL = 300
    ANIMATION_SLOW = 500
    ANIMATION_VERY_SLOW = 1000
    
    # Z-индексы
    Z_INDEX_BASE = 0
    Z_INDEX_DROPDOWN = 1000
    Z_INDEX_STICKY = 1100
    Z_INDEX_FIXED = 1200
    Z_INDEX_MODAL_BACKDROP = 1300
    Z_INDEX_MODAL = 2000
    Z_INDEX_POPOVER = 3000
    Z_INDEX_TOOLTIP = 4000
    Z_INDEX_NOTIFICATION = 5000
    
    # Прозрачность
    OPACITY_0 = 0.0
    OPACITY_DISABLED = 0.5
    OPACITY_HOVER = 0.8
    OPACITY_ACTIVE = 1.0
    
    # Брейкпоинты
    BREAKPOINT_MOBILE = 480
    BREAKPOINT_TABLET = 768
    BREAKPOINT_DESKTOP = 1024
    BREAKPOINT_WIDE = 1280
    BREAKPOINT_ULTRAWIDE = 1920
    
    # ===== МЕТОДЫ УТИЛИТЫ =====
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """
        Получить цвет для статуса
        
        Args:
            status: Название статуса
            
        Returns:
            str: HEX код цвета
        """
        status_colors = {
            'active': cls.STATUS_ACTIVE,
            'expired': cls.STATUS_EXPIRED,
            'blocked': cls.STATUS_BLOCKED,
            'created': cls.STATUS_PENDING,
            'pending': cls.STATUS_PENDING,
            'warning': cls.STATUS_WARNING,
            'info': cls.STATUS_INFO,
            'success': cls.STATUS_SUCCESS,
            'error': cls.STATUS_ERROR,
            'processing': cls.STATUS_PROCESSING,
            'unknown': cls.STATUS_UNKNOWN
        }
        return status_colors.get(status.lower(), cls.TEXT_SECONDARY)
    
    @classmethod
    def get_hover_color(cls, base_color: str) -> str:
        """
        Получить цвет при наведении
        
        Args:
            base_color: Базовый цвет
            
        Returns:
            str: HEX код цвета при наведении
        """
        # Простая логика: делаем цвет светлее
        if base_color.startswith('#'):
            # Преобразуем в RGB
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
            
            # Делаем светлее на 20%
            r = min(255, int(r * 1.2))
            g = min(255, int(g * 1.2))
            b = min(255, int(b * 1.2))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        return base_color
    
    @classmethod
    def apply_opacity(cls, color: str, opacity: float) -> str:
        """
        Применить прозрачность к цвету
        
        Args:
            color: HEX цвет
            opacity: Прозрачность (0.0 - 1.0)
            
        Returns:
            str: RGBA цвет
        """
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"rgba({r}, {g}, {b}, {opacity})"
        return color
    
    @classmethod
    def darken_color(cls, color: str, amount: float = 0.2) -> str:
        """
        Затемнить цвет
        
        Args:
            color: HEX цвет
            amount: Степень затемнения (0.0 - 1.0)
            
        Returns:
            str: HEX код затемненного цвета
        """
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # Затемняем
            r = max(0, int(r * (1 - amount)))
            g = max(0, int(g * (1 - amount)))
            b = max(0, int(b * (1 - amount)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    @classmethod
    def lighten_color(cls, color: str, amount: float = 0.2) -> str:
        """
        Осветлить цвет
        
        Args:
            color: HEX цвет
            amount: Степень осветления (0.0 - 1.0)
            
        Returns:
            str: HEX код осветленного цвета
        """
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # Осветляем
            r = min(255, r + int((255 - r) * amount))
            g = min(255, g + int((255 - g) * amount))
            b = min(255, b + int((255 - b) * amount))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        return color