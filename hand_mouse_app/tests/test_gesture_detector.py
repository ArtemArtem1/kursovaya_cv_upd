from app.gesture_detector import GestureDetector


def test_get_point_returns_correct_coordinates():
    detector = GestureDetector()

    landmarks = [
        (0, 10, 20),
        (4, 30, 40),
        (8, 50, 60),
    ]

    assert detector.get_point(landmarks, 8) == (50, 60)


def test_distance_between_two_points():
    detector = GestureDetector()

    result = detector.distance((0, 0), (3, 4))

    assert result == 5


def test_is_finger_up_returns_true_when_tip_above_pip():
    detector = GestureDetector()

    landmarks = [
        (8, 100, 50),
        (6, 100, 100),
    ]

    assert detector.is_finger_up(landmarks, 8, 6) is True


def test_detect_right_click_gesture():
    detector = GestureDetector(click_distance=35)

    landmarks = [
        (4, 10, 200),

        (8, 100, 50),
        (6, 100, 100),

        (12, 130, 130),
        (10, 130, 100),

        (16, 160, 130),
        (14, 160, 100),

        (20, 190, 50),
        (18, 190, 100),
    ]

    result = detector.detect(landmarks)

    assert result["mode"] == "RIGHT_CLICK"