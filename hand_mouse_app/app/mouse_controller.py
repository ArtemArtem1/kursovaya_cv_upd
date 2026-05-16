import pyautogui


class MouseController:
    """
    Класс отвечает за управление курсором мыши.
    """

    def __init__(self):
        pyautogui.FAILSAFE = False

        self.screen_width, self.screen_height = pyautogui.size()

        self.prev_x = 0
        self.prev_y = 0

    def move_cursor(
        self,
        finger_x,
        finger_y,
        frame_width,
        frame_height,
        sensitivity=1.0,
        smoothing=5,
        margin_x=100,
        margin_y=80
    ):
        """
        Перемещает курсор по координатам указательного пальца.

        finger_x, finger_y — координаты пальца в кадре камеры.
        frame_width, frame_height — размер изображения с камеры.
        margin_x, margin_y — отступы активной зоны от краёв камеры.
        """

        # Границы активной области
        left = margin_x
        right = frame_width - margin_x
        top = margin_y
        bottom = frame_height - margin_y

        # Защита от неправильных значений
        if right <= left or bottom <= top:
            left = 0
            right = frame_width
            top = 0
            bottom = frame_height

        # Ограничиваем палец активной областью
        finger_x = max(left, min(finger_x, right))
        finger_y = max(top, min(finger_y, bottom))

        # Перевод координат активной зоны камеры в координаты экрана
        # По X делаем зеркально, потому что камера отображается как зеркало
        screen_x = (finger_x - left) * self.screen_width / (right - left)

        screen_y = (
            (finger_y - top) * self.screen_height / (bottom - top)
        )

        # Применяем чувствительность
        screen_x = self.prev_x + (screen_x - self.prev_x) * sensitivity
        screen_y = self.prev_y + (screen_y - self.prev_y) * sensitivity

        # Сглаживание
        current_x = self.prev_x + (screen_x - self.prev_x) / smoothing
        current_y = self.prev_y + (screen_y - self.prev_y) / smoothing

        pyautogui.moveTo(current_x, current_y)

        self.prev_x = current_x
        self.prev_y = current_y

    def left_click(self):
        pyautogui.click(button="left")

    def right_click(self):
        pyautogui.click(button="right")

    def scroll(self, amount):
        pyautogui.scroll(amount)