import sys
import types


# Заглушка matplotlib для собранного exe.
# MediaPipe пытается импортировать matplotlib через drawing_utils,
# но в нашем приложении matplotlib реально не используется.
if "matplotlib" not in sys.modules:
    matplotlib_stub = types.ModuleType("matplotlib")
    pyplot_stub = types.ModuleType("matplotlib.pyplot")

    def dummy_function(*args, **kwargs):
        return None

    pyplot_stub.plot = dummy_function
    pyplot_stub.show = dummy_function
    pyplot_stub.figure = dummy_function
    pyplot_stub.imshow = dummy_function
    pyplot_stub.axis = dummy_function
    pyplot_stub.title = dummy_function
    pyplot_stub.get_cmap = dummy_function

    sys.modules["matplotlib"] = matplotlib_stub
    sys.modules["matplotlib.pyplot"] = pyplot_stub

import cv2
import mediapipe as mp


class HandTracker:
    """
    Класс отвечает за распознавание руки в кадре.
    Используется модель MediaPipe Hands.
    Отрисовка точек выполняется вручную через OpenCV,
    чтобы не использовать mediapipe.solutions.drawing_utils.
    """

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.max_hands = max_hands

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def draw_hand(self, frame, landmarks):
        """
        Рисует точки и линии руки вручную через OpenCV.
        """

        # Рисуем линии между точками
        for connection in self.mp_hands.HAND_CONNECTIONS:
            start_id = connection[0]
            end_id = connection[1]

            start_point = None
            end_point = None

            for lm_id, x, y in landmarks:
                if lm_id == start_id:
                    start_point = (x, y)
                elif lm_id == end_id:
                    end_point = (x, y)

            if start_point is not None and end_point is not None:
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)

        # Рисуем точки
        for lm_id, x, y in landmarks:
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

    def find_hand_landmarks(self, frame):
        """
        Находит ключевые точки руки.

        Возвращает:
        - frame: кадр с нарисованными точками руки
        - landmarks: список точек руки [(id, x, y), ...]
        """

        landmarks = []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                height, width, _ = frame.shape

                for point_id, lm in enumerate(hand_landmarks.landmark):
                    x = int(lm.x * width)
                    y = int(lm.y * height)
                    landmarks.append((point_id, x, y))

                self.draw_hand(frame, landmarks)

                # Берём только одну руку
                break

        return frame, landmarks