class AppConfig:
    def __init__(self):
        self.camera_index = 0

        self.mouse_enabled = True

        # Включение/отключение отдельных жестов
        self.left_click_enabled = True
        self.right_click_enabled = True
        self.scroll_enabled = True

        # Чем больше значение, тем быстрее курсор
        self.sensitivity = 1.0

        # Сглаживание движения курсора
        self.smoothing = 8

        # Порог расстояния между пальцами для клика
        self.click_distance = 35

        # Задержка между кликами в кадрах
        self.click_cooldown_frames = 15

        # Границы активной области камеры
        self.frame_margin_x = 100
        self.frame_margin_y = 80

        # Время удержания жеста левого клика для зажатия кнопки
        self.left_hold_time = 0.5