import math
import time


class GestureDetector:
    """
    Класс определяет жесты по координатам точек руки.
    """

    WRIST = 0

    THUMB_TIP = 4

    INDEX_TIP = 8
    INDEX_PIP = 6

    MIDDLE_TIP = 12
    MIDDLE_PIP = 10

    RING_TIP = 16
    RING_PIP = 14

    PINKY_TIP = 20
    PINKY_PIP = 18

    def __init__(self, click_distance=35, click_cooldown_frames=15, left_hold_time=1.0):
        self.click_distance = click_distance
        self.click_cooldown_frames = click_cooldown_frames
        self.left_hold_time = left_hold_time

        self.cooldown = 0

        self.prev_scroll_y = None

        # Состояние удержания левого клика
        self.pinching = False
        self.pinch_start_time = None
        self.dragging = False
        self.click_sent_for_current_pinch = False

    def update_settings(self, click_distance=None, click_cooldown_frames=None, left_hold_time=None):
        if click_distance is not None:
            self.click_distance = click_distance

        if click_cooldown_frames is not None:
            self.click_cooldown_frames = click_cooldown_frames

        if left_hold_time is not None:
            self.left_hold_time = left_hold_time

    def get_point(self, landmarks, point_id):
        for lm_id, x, y in landmarks:
            if lm_id == point_id:
                return x, y

        return None

    def distance(self, p1, p2):
        if p1 is None or p2 is None:
            return 9999

        x1, y1 = p1
        x2, y2 = p2

        return math.hypot(x2 - x1, y2 - y1)

    def is_finger_up(self, landmarks, tip_id, pip_id):
        tip = self.get_point(landmarks, tip_id)
        pip = self.get_point(landmarks, pip_id)

        if tip is None or pip is None:
            return False

        return tip[1] < pip[1]

    def reset_left_hold(self):
        self.pinching = False
        self.pinch_start_time = None
        self.dragging = False
        self.click_sent_for_current_pinch = False

    def detect(self, landmarks):
        """
        Возвращает:
        MOVE             — перемещение курсора
        LEFT_CLICK       — короткий левый клик
        LEFT_HOLD_START  — начало зажатия левой кнопки
        LEFT_HOLD_MOVE   — движение с зажатой левой кнопкой
        LEFT_HOLD_END    — отпускание левой кнопки
        RIGHT_CLICK      — правый клик
        SCROLL           — прокрутка
        NONE             — рука не найдена
        """

        if self.cooldown > 0:
            self.cooldown -= 1

        if not landmarks:
            if self.dragging:
                self.reset_left_hold()

                return {
                    "mode": "LEFT_HOLD_END",
                    "index_pos": None,
                    "scroll_amount": 0,
                    "distance": None
                }

            self.reset_left_hold()
            self.prev_scroll_y = None

            return {
                "mode": "NONE",
                "index_pos": None,
                "scroll_amount": 0,
                "distance": None
            }

        thumb_tip = self.get_point(landmarks, self.THUMB_TIP)
        index_tip = self.get_point(landmarks, self.INDEX_TIP)

        index_up = self.is_finger_up(landmarks, self.INDEX_TIP, self.INDEX_PIP)
        middle_up = self.is_finger_up(landmarks, self.MIDDLE_TIP, self.MIDDLE_PIP)
        ring_up = self.is_finger_up(landmarks, self.RING_TIP, self.RING_PIP)
        pinky_up = self.is_finger_up(landmarks, self.PINKY_TIP, self.PINKY_PIP)

        left_click_distance = self.distance(thumb_tip, index_tip)
        is_left_pinch = left_click_distance < self.click_distance

        # -------------------------------
        # Левый клик / зажатие левой кнопки
        # -------------------------------

        if is_left_pinch:
            self.prev_scroll_y = None

            # Щипок только начался
            if not self.pinching:
                self.pinching = True
                self.pinch_start_time = time.time()
                self.click_sent_for_current_pinch = True

                return {
                    "mode": "LEFT_CLICK",
                    "index_pos": index_tip,
                    "scroll_amount": 0,
                    "distance": left_click_distance
                }

            hold_duration = time.time() - self.pinch_start_time

            # Если щипок удерживается дольше заданного времени — начинаем зажатие
            if hold_duration >= self.left_hold_time:
                if not self.dragging:
                    self.dragging = True

                    return {
                        "mode": "LEFT_HOLD_START",
                        "index_pos": index_tip,
                        "scroll_amount": 0,
                        "distance": left_click_distance
                    }

                return {
                    "mode": "LEFT_HOLD_MOVE",
                    "index_pos": index_tip,
                    "scroll_amount": 0,
                    "distance": left_click_distance
                }

            # Пока щипок удерживается, но время удержания ещё не прошло
            return {
                "mode": "MOVE",
                "index_pos": index_tip,
                "scroll_amount": 0,
                "distance": left_click_distance
            }

        # Если щипок отпустили
        if self.pinching:
            was_dragging = self.dragging

            self.reset_left_hold()

            if was_dragging:
                self.cooldown = self.click_cooldown_frames

                return {
                    "mode": "LEFT_HOLD_END",
                    "index_pos": index_tip,
                    "scroll_amount": 0,
                    "distance": left_click_distance
                }

            self.cooldown = self.click_cooldown_frames

            return {
                "mode": "MOVE",
                "index_pos": index_tip,
                "scroll_amount": 0,
                "distance": left_click_distance
            }

        # -------------------------------
        # Правый клик: жест "коза"
        # -------------------------------

        if index_up and pinky_up and not middle_up and not ring_up and self.cooldown == 0:
            self.cooldown = self.click_cooldown_frames
            self.prev_scroll_y = None

            return {
                "mode": "RIGHT_CLICK",
                "index_pos": index_tip,
                "scroll_amount": 0,
                "distance": None
            }

        # -------------------------------
        # Скролл: указательный + средний
        # -------------------------------

        if index_up and middle_up and not ring_up and not pinky_up:
            middle_tip = self.get_point(landmarks, self.MIDDLE_TIP)

            if index_tip is not None and middle_tip is not None:
                current_scroll_y = (index_tip[1] + middle_tip[1]) / 2

                if self.prev_scroll_y is None:
                    self.prev_scroll_y = current_scroll_y
                    scroll_amount = 0
                else:
                    delta_y = self.prev_scroll_y - current_scroll_y

                    scroll_amount = int(delta_y / 3)

                    self.prev_scroll_y = current_scroll_y

                return {
                    "mode": "SCROLL",
                    "index_pos": index_tip,
                    "scroll_amount": scroll_amount,
                    "distance": None
                }

        self.prev_scroll_y = None

        return {
            "mode": "MOVE",
            "index_pos": index_tip,
            "scroll_amount": 0,
            "distance": left_click_distance
        }