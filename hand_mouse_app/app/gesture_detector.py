import math


class GestureDetector:
    """
    Класс определяет жесты по координатам точек руки.
    """

    # Номера точек MediaPipe
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12

    def __init__(self, click_distance=35, click_cooldown_frames=15):
        self.click_distance = click_distance
        self.click_cooldown_frames = click_cooldown_frames

        self.cooldown = 0

    def update_settings(self, click_distance=None, click_cooldown_frames=None):
        if click_distance is not None:
            self.click_distance = click_distance

        if click_cooldown_frames is not None:
            self.click_cooldown_frames = click_cooldown_frames

    def get_point(self, landmarks, point_id):
        """
        Получает точку руки по её номеру.
        """
        for lm_id, x, y in landmarks:
            if lm_id == point_id:
                return x, y

        return None

    def distance(self, p1, p2):
        """
        Считает расстояние между двумя точками.
        """
        if p1 is None or p2 is None:
            return 9999

        x1, y1 = p1
        x2, y2 = p2

        return math.hypot(x2 - x1, y2 - y1)

    def detect(self, landmarks):
        """
        Определяет текущий жест.

        Возвращает словарь:
        {
            "mode": "MOVE" / "LEFT_CLICK" / "NONE",
            "index_pos": (x, y),
            "distance": число
        }
        """

        if not landmarks:
            return {
                "mode": "NONE",
                "index_pos": None,
                "distance": None
            }

        thumb_tip = self.get_point(landmarks, self.THUMB_TIP)
        index_tip = self.get_point(landmarks, self.INDEX_TIP)

        pinch_distance = self.distance(thumb_tip, index_tip)

        if self.cooldown > 0:
            self.cooldown -= 1

        # Жест щипка: большой и указательный пальцы близко
        if pinch_distance < self.click_distance and self.cooldown == 0:
            self.cooldown = self.click_cooldown_frames

            return {
                "mode": "LEFT_CLICK",
                "index_pos": index_tip,
                "distance": pinch_distance
            }

        return {
            "mode": "MOVE",
            "index_pos": index_tip,
            "distance": pinch_distance
        }