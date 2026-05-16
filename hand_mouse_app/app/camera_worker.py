import cv2

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from .hand_tracker import HandTracker
from .gesture_detector import GestureDetector
from .mouse_controller import MouseController


class CameraWorker(QThread):
    """
    Поток камеры.
    Нужен, чтобы интерфейс не зависал при обработке видео.
    """

    frame_ready = Signal(QImage)
    status_changed = Signal(str)

    def __init__(self, config):
        super().__init__()

        self.config = config
        self.running = False

        self.hand_tracker = HandTracker()
        self.gesture_detector = GestureDetector(
            click_distance=self.config.click_distance,
            click_cooldown_frames=self.config.click_cooldown_frames
        )
        self.mouse_controller = MouseController()

    def run(self):
        self.running = True

        cap = cv2.VideoCapture(self.config.camera_index)

        if not cap.isOpened():
            self.status_changed.emit("Ошибка: камера не найдена")
            return

        self.status_changed.emit("Камера запущена")

        while self.running:
            success, frame = cap.read()

            if not success:
                self.status_changed.emit("Ошибка чтения кадра")
                break

            # Зеркальное отображение, чтобы было удобнее управлять
            frame = cv2.flip(frame, 1)

            frame_height, frame_width, _ = frame.shape

            # Рисуем активную область управления
            left = self.config.frame_margin_x
            right = frame_width - self.config.frame_margin_x
            top = self.config.frame_margin_y
            bottom = frame_height - self.config.frame_margin_y

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (255, 0, 0),
                2
            )

            frame, landmarks = self.hand_tracker.find_hand_landmarks(frame)

            gesture = self.gesture_detector.detect(landmarks)

            mode = gesture["mode"]
            index_pos = gesture["index_pos"]

            if mode == "MOVE":
                self.status_changed.emit("Режим: перемещение")

                if self.config.mouse_enabled and index_pos is not None:
                    x, y = index_pos

                    self.mouse_controller.move_cursor(
                        finger_x=x,
                        finger_y=y,
                        frame_width=frame_width,
                        frame_height=frame_height,
                        sensitivity=self.config.sensitivity,
                        smoothing=self.config.smoothing,
                        margin_x=self.config.frame_margin_x,
                        margin_y=self.config.frame_margin_y
                    )

            elif mode == "LEFT_CLICK":
                self.status_changed.emit("Режим: левый клик")

                if self.config.mouse_enabled:
                    self.mouse_controller.left_click()

            else:
                self.status_changed.emit("Режим: рука не найдена")

            # Выводим подсказку на изображение
            cv2.putText(
                frame,
                f"Mode: {mode}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # Конвертация кадра OpenCV в QImage для PySide6
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape

            bytes_per_line = ch * w

            qt_image = QImage(
                rgb_frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format_RGB888
            ).copy()

            self.frame_ready.emit(qt_image)

        cap.release()
        self.status_changed.emit("Камера остановлена")

    def stop(self):
        self.running = False
        self.wait()