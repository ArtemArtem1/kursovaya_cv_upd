from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QSlider,
    QSpinBox,
    QGroupBox,
    QFormLayout,
    QDialog,
    QDialogButtonBox
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from app.config import AppConfig
from app.camera_worker import CameraWorker


class SettingsDialog(QDialog):
    """
    Окно настроек приложения.
    """

    def __init__(self, config, camera_worker=None, parent=None):
        super().__init__(parent)

        self.config = config
        self.camera_worker = camera_worker

        self.setWindowTitle("Настройки")
        self.setMinimumWidth(450)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Жесты
        gestures_group = QGroupBox("Жесты")
        gestures_layout = QVBoxLayout()

        self.left_click_checkbox = QCheckBox("Левый клик")
        self.left_click_checkbox.setChecked(self.config.left_click_enabled)
        self.left_click_checkbox.stateChanged.connect(self.toggle_left_click)

        self.right_click_checkbox = QCheckBox("Правый клик")
        self.right_click_checkbox.setChecked(self.config.right_click_enabled)
        self.right_click_checkbox.stateChanged.connect(self.toggle_right_click)

        self.scroll_checkbox = QCheckBox("Прокрутка колесиком")
        self.scroll_checkbox.setChecked(self.config.scroll_enabled)
        self.scroll_checkbox.stateChanged.connect(self.toggle_scroll)

        gestures_layout.addWidget(self.left_click_checkbox)
        gestures_layout.addWidget(self.right_click_checkbox)
        gestures_layout.addWidget(self.scroll_checkbox)

        gestures_group.setLayout(gestures_layout)
        main_layout.addWidget(gestures_group)

        # Настройки управления
        settings_group = QGroupBox("Параметры управления")
        settings_layout = QFormLayout()

        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(1)
        self.sensitivity_slider.setMaximum(20)
        self.sensitivity_slider.setValue(int(self.config.sensitivity * 10))
        self.sensitivity_slider.valueChanged.connect(self.change_sensitivity)

        self.sensitivity_label = QLabel(str(self.config.sensitivity))

        sensitivity_row = QHBoxLayout()
        sensitivity_row.addWidget(self.sensitivity_slider)
        sensitivity_row.addWidget(self.sensitivity_label)

        settings_layout.addRow("Чувствительность:", sensitivity_row)

        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setMinimum(1)
        self.smoothing_slider.setMaximum(15)
        self.smoothing_slider.setValue(self.config.smoothing)
        self.smoothing_slider.valueChanged.connect(self.change_smoothing)

        self.smoothing_label = QLabel(str(self.config.smoothing))

        smoothing_row = QHBoxLayout()
        smoothing_row.addWidget(self.smoothing_slider)
        smoothing_row.addWidget(self.smoothing_label)

        settings_layout.addRow("Сглаживание:", smoothing_row)

        self.click_distance_slider = QSlider(Qt.Horizontal)
        self.click_distance_slider.setMinimum(10)
        self.click_distance_slider.setMaximum(80)
        self.click_distance_slider.setValue(self.config.click_distance)
        self.click_distance_slider.valueChanged.connect(self.change_click_distance)

        self.click_distance_label = QLabel(str(self.config.click_distance))

        click_row = QHBoxLayout()
        click_row.addWidget(self.click_distance_slider)
        click_row.addWidget(self.click_distance_label)

        settings_layout.addRow("Порог клика:", click_row)

        self.margin_x_slider = QSlider(Qt.Horizontal)
        self.margin_x_slider.setMinimum(0)
        self.margin_x_slider.setMaximum(250)
        self.margin_x_slider.setValue(self.config.frame_margin_x)
        self.margin_x_slider.valueChanged.connect(self.change_margin_x)

        self.margin_x_label = QLabel(str(self.config.frame_margin_x))

        margin_x_row = QHBoxLayout()
        margin_x_row.addWidget(self.margin_x_slider)
        margin_x_row.addWidget(self.margin_x_label)

        settings_layout.addRow("Граница X:", margin_x_row)

        self.margin_y_slider = QSlider(Qt.Horizontal)
        self.margin_y_slider.setMinimum(0)
        self.margin_y_slider.setMaximum(200)
        self.margin_y_slider.setValue(self.config.frame_margin_y)
        self.margin_y_slider.valueChanged.connect(self.change_margin_y)

        self.margin_y_label = QLabel(str(self.config.frame_margin_y))

        margin_y_row = QHBoxLayout()
        margin_y_row.addWidget(self.margin_y_slider)
        margin_y_row.addWidget(self.margin_y_label)

        settings_layout.addRow("Граница Y:", margin_y_row)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)

        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def toggle_left_click(self, state):
        self.config.left_click_enabled = state == Qt.Checked.value

    def toggle_right_click(self, state):
        self.config.right_click_enabled = state == Qt.Checked.value

    def toggle_scroll(self, state):
        self.config.scroll_enabled = state == Qt.Checked.value

    def change_sensitivity(self, value):
        self.config.sensitivity = value / 10
        self.sensitivity_label.setText(str(self.config.sensitivity))

    def change_smoothing(self, value):
        self.config.smoothing = value
        self.smoothing_label.setText(str(value))

    def change_click_distance(self, value):
        self.config.click_distance = value
        self.click_distance_label.setText(str(value))

        if self.camera_worker is not None:
            self.camera_worker.gesture_detector.update_settings(
                click_distance=value
            )

    def change_margin_x(self, value):
        self.config.frame_margin_x = value
        self.margin_x_label.setText(str(value))

    def change_margin_y(self, value):
        self.config.frame_margin_y = value
        self.margin_y_label.setText(str(value))


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Virtual Hand Mouse")
        self.setMinimumSize(1000, 650)

        self.config = AppConfig()
        self.camera_worker = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Область видео
        self.video_label = QLabel("Камера не запущена")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #222;
                color: white;
                font-size: 20px;
                border-radius: 8px;
            }
        """)

        main_layout.addWidget(self.video_label, stretch=3)

        # Панель управления
        control_panel = QVBoxLayout()

        title = QLabel("Virtual Hand Mouse")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        control_panel.addWidget(title)

        self.status_label = QLabel("Статус: ожидание")
        self.status_label.setWordWrap(True)
        control_panel.addWidget(self.status_label)

        # Камера
        camera_group = QGroupBox("Камера")
        camera_layout = QFormLayout()

        self.camera_spinbox = QSpinBox()
        self.camera_spinbox.setMinimum(0)
        self.camera_spinbox.setMaximum(10)
        self.camera_spinbox.setValue(self.config.camera_index)
        self.camera_spinbox.valueChanged.connect(self.change_camera_index)

        camera_layout.addRow("Номер камеры:", self.camera_spinbox)

        self.start_button = QPushButton("Запустить камеру")
        self.start_button.clicked.connect(self.start_camera)

        self.stop_button = QPushButton("Остановить камеру")
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)

        camera_layout.addRow(self.start_button)
        camera_layout.addRow(self.stop_button)

        camera_group.setLayout(camera_layout)
        control_panel.addWidget(camera_group)

        # Управление мышью
        mouse_group = QGroupBox("Управление")
        mouse_layout = QVBoxLayout()

        self.mouse_checkbox = QCheckBox("Включить управление курсором")
        self.mouse_checkbox.setChecked(self.config.mouse_enabled)
        self.mouse_checkbox.stateChanged.connect(self.toggle_mouse_control)

        self.settings_button = QPushButton("Настройки")
        self.settings_button.clicked.connect(self.open_settings)

        mouse_layout.addWidget(self.mouse_checkbox)
        mouse_layout.addWidget(self.settings_button)

        mouse_group.setLayout(mouse_layout)
        control_panel.addWidget(mouse_group)

        # Описание жестов
        info_group = QGroupBox("Жесты")
        info_layout = QVBoxLayout()

        info_label = QLabel(
            "Движение указательного пальца — перемещение курсора\n"
            "Большой + указательный палец — левый клик\n"
            "Указательный + мизинец подняты — правый клик\n"
            "Указательный + средний подняты — прокрутка\n\n"
            "Настройки жестов доступны по кнопке «Настройки»."
        )
        info_label.setWordWrap(True)

        info_layout.addWidget(info_label)

        info_group.setLayout(info_layout)
        control_panel.addWidget(info_group)

        control_panel.addStretch()

        main_layout.addLayout(control_panel, stretch=1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def start_camera(self):
        if self.camera_worker is not None and self.camera_worker.isRunning():
            return

        self.camera_worker = CameraWorker(self.config)
        self.camera_worker.frame_ready.connect(self.update_frame)
        self.camera_worker.status_changed.connect(self.update_status)

        self.camera_worker.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.camera_spinbox.setEnabled(False)

    def stop_camera(self):
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker = None

        self.video_label.setText("Камера остановлена")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.camera_spinbox.setEnabled(True)

    def open_settings(self):
        dialog = SettingsDialog(
            config=self.config,
            camera_worker=self.camera_worker,
            parent=self
        )
        dialog.exec()

    def update_frame(self, image):
        pixmap = QPixmap.fromImage(image)

        scaled_pixmap = pixmap.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.video_label.setPixmap(scaled_pixmap)

    def update_status(self, text):
        self.status_label.setText(f"Статус: {text}")

    def change_camera_index(self, value):
        self.config.camera_index = value

    def toggle_mouse_control(self, state):
        self.config.mouse_enabled = state == Qt.Checked.value

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()