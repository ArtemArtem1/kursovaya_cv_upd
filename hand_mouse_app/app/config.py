class AppConfig:
    def __init__(self):
        self.camera_index = 0

        self.mouse_enabled = True

        # Чем больше значение, тем быстрее курсор
        self.sensitivity = 1.0

        # Сглаживание движения курсора
        # 1 — почти без сглаживания
        # 10 — очень плавно, но с задержкой
        self.smoothing = 5

        # Порог расстояния между большим и указательным пальцем для клика
        self.click_distance = 35

        # Задержка между кликами в кадрах
        self.click_cooldown_frames = 15