import cv2
import mediapipe as mp


class HandTracker:
    """
    Класс отвечает за распознавание руки в кадре.
    Используется модель MediaPipe Hands.
    """

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.max_hands = max_hands

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def find_hand_landmarks(self, frame):
        """
        Находит ключевые точки руки.

        Возвращает:
        - frame: кадр с нарисованными точками руки
        - landmarks: список точек руки [(id, x, y), ...]
        """

        landmarks = []

        # OpenCV использует BGR, а MediaPipe — RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                height, width, _ = frame.shape

                for point_id, lm in enumerate(hand_landmarks.landmark):
                    x = int(lm.x * width)
                    y = int(lm.y * height)
                    landmarks.append((point_id, x, y))

                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                # Берём только одну руку
                break

        return frame, landmarks