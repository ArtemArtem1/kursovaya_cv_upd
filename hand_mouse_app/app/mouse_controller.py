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

    def move_cursor(self, finger_x, finger_y, frame_width, frame_height, sensitivity=1.0, smoothing=5):
        """
        Перемещает курсор по координатам указательного пальца.

        finger_x, finger_y — координаты пальца в кадре камеры.
        frame_width, frame_height — размер изображения с камеры.
        """

        # Перевод координат камеры в координаты экрана
        screen_x = self.screen_width - (finger_x * self.screen_width / frame_width)
        screen_y = finger_y * self.screen_height / frame_height

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