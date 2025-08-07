import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QSlider, QProgressBar, QHBoxLayout
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from internal.timer.timer import Timer
from internal.media.media import MediaManager
from internal.settings.settings import SettingsDialog

class PomodoroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setGeometry(100, 100, 800, 800)

        # Инициализация компонентов
        self.timer = Timer()
        self.media = MediaManager("assets/images", "assets/music")
        self.is_muted = False

        # Таймер для обновления
        self.qt_timer = QTimer(self)
        self.qt_timer.timeout.connect(self.update_timer)

        # GUI элементы
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.update_background()

        # --- Полупрозрачная панель и затемнение ---
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background-color: rgba(30, 30, 30, 120); border-radius: 30px;")
        self.overlay.setGeometry(80, 100, 640, 600)
        self.overlay.lower()

        self.panel = QWidget(self)
        self.panel.setGeometry(80, 100, 640, 600)
        self.panel.setStyleSheet("""
            background-color: rgba(245, 245, 245, 220);
            border-radius: 30px;
        """)

        # Таймер и прогресс-бар
        self.time_label = QLabel(self.timer.get_time_display(), self.panel)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            font-size: 80px;
            color: #222;
            font-weight: bold;
            text-shadow: 1px 1px 6px #fff, 0 0 2px #2193b0;
        """)

        self.progress_label = QLabel("Прогресс", self.panel)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 16px; color: #2193b0; font-weight: bold; margin-bottom: 2px;")

        self.progress_bar = QProgressBar(self.panel)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.timer.get_total_seconds())
        self.progress_bar.setValue(self.timer.get_total_seconds())
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2193b0;
                border-radius: 10px;
                background: #e0eafc;
                height: 26px;
                margin-bottom: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6dd5ed, stop:1 #2193b0
                );
                border-radius: 10px;
            }
        """)

        # Кнопки
        self.start_button = QPushButton("Старт", self.panel)
        self.start_button.clicked.connect(self.toggle_timer)

        self.work_button = QPushButton("К работе", self.panel)
        self.work_button.clicked.connect(self.start_work)
        self.work_button.setEnabled(False)

        self.break_button = QPushButton("Отдых", self.panel)
        self.break_button.clicked.connect(self.start_break)
        self.break_button.setEnabled(True)

        self.change_bg_button = QPushButton("Сменить фон", self.panel)
        self.change_bg_button.clicked.connect(self.change_background)

        self.settings_button = QPushButton("Настройки", self.panel)
        self.settings_button.clicked.connect(self.open_settings)

        self.mute_button = QPushButton("Mute", self.panel)
        self.mute_button.clicked.connect(self.toggle_mute)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal, self.panel)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # --- Минимализм: выпадающее меню ---
        self.menu_button = QPushButton("≡ Меню", self.panel)
        self.menu_button.clicked.connect(self.toggle_menu)
        self.menu_visible = False

        # --- Переключатель темы ---
        self.theme_button = QPushButton("Тема: Светлая", self.panel)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.is_dark_theme = False

        # Второстепенные кнопки (только в меню)
        self.secondary_buttons = [
            self.change_bg_button, self.settings_button, self.volume_slider, self.mute_button
        ]
        for btn in self.secondary_buttons:
            btn.hide()

        # Новый стиль для компактных кнопок
        button_style = """
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6dd5ed, stop:1 #2193b0
                );
                color: white;
                border-radius: 12px;
                border: 1px solid #2193b0;
                font-size: 16px;
                padding: 4px 12px;
                min-height: 28px;
                min-width: 90px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2193b0, stop:1 #6dd5ed
                );
                border: 1px solid #6dd5ed;
            }
            QPushButton:pressed {
                background-color: #17627a;
            }
        """
        for btn in [
            self.start_button, self.work_button, self.break_button,
            self.change_bg_button, self.settings_button, self.mute_button,
            self.menu_button, self.theme_button
        ]:
            btn.setStyleSheet(button_style)

        # Основные кнопки в одну строку
        main_buttons_layout = QHBoxLayout()
        main_buttons_layout.setSpacing(12)
        main_buttons_layout.addWidget(self.start_button)
        main_buttons_layout.addWidget(self.work_button)
        main_buttons_layout.addWidget(self.break_button)

        # Нижняя строка: меню и тема
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setSpacing(10)
        bottom_buttons_layout.addWidget(self.menu_button)
        bottom_buttons_layout.addWidget(self.theme_button)

        # Громкость и mute в одну строку (только для меню)
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(8)
        volume_label = QLabel("Громкость:")
        volume_label.setStyleSheet("font-size: 15px; color: #222;")
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.mute_button)

        # Строка для второстепенных кнопок (появляется только при открытом меню)
        secondary_buttons_layout = QHBoxLayout()
        secondary_buttons_layout.setSpacing(10)
        secondary_buttons_layout.addWidget(self.change_bg_button)
        secondary_buttons_layout.addWidget(self.settings_button)
        secondary_buttons_layout.addLayout(volume_layout)

        # Макет панели
        panel_layout = QVBoxLayout()
        panel_layout.setSpacing(18)
        panel_layout.setContentsMargins(32, 32, 32, 32)
        panel_layout.addWidget(self.time_label)
        panel_layout.addWidget(self.progress_label)
        panel_layout.addWidget(self.progress_bar)
        panel_layout.addSpacing(10)
        panel_layout.addLayout(main_buttons_layout)
        panel_layout.addSpacing(10)
        panel_layout.addLayout(bottom_buttons_layout)
        panel_layout.addSpacing(10)
        panel_layout.addLayout(secondary_buttons_layout)
        self.panel.setLayout(panel_layout)

        self.setCentralWidget(self.bg_label)

    def toggle_menu(self):
        self.menu_visible = not self.menu_visible
        for btn in self.secondary_buttons:
            btn.setVisible(self.menu_visible)

    def toggle_theme(self):
        if not self.is_dark_theme:
            self.panel.setStyleSheet("background-color: rgba(34,34,34,220); border-radius: 30px;")
            self.time_label.setStyleSheet("""
                font-size: 80px; color: #fff; font-weight: bold;
                text-shadow: 1px 1px 6px #000, 0 0 2px #2193b0;
            """)
            self.theme_button.setText("Тема: Тёмная")
            self.is_dark_theme = True
        else:
            self.panel.setStyleSheet("background-color: rgba(245,245,245,220); border-radius: 30px;")
            self.time_label.setStyleSheet("""
                font-size: 80px; color: #222; font-weight: bold;
                text-shadow: 1px 1px 6px #fff, 0 0 2px #2193b0;
            """)
            self.theme_button.setText("Тема: Светлая")
            self.is_dark_theme = False
        # Восстановить видимость второстепенных кнопок после смены темы
        for btn in self.secondary_buttons:
            btn.setVisible(self.menu_visible)

    def update_background(self):
        pixmap = QPixmap(self.media.get_current_image())
        self.bg_label.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        self.update_background()
        # Центрируем панель и затемнение
        w, h = 640, 600
        x = (self.width() - w) // 2
        y = (self.height() - h) // 2
        self.overlay.setGeometry(x, y, w, h)
        self.panel.setGeometry(x, y, w, h)
        super().resizeEvent(event)

    def change_background(self):
        self.media.next_image()
        self.update_background()
        # Восстановить видимость второстепенных кнопок после смены фона
        for btn in self.secondary_buttons:
            btn.setVisible(self.menu_visible)

    def set_volume(self, value):
        self.media.set_volume(value)
        self.is_muted = False
        self.mute_button.setText("Mute")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.media.toggle_mute(self.is_muted)
        self.mute_button.setText("Unmute" if self.is_muted else "Mute")

    def toggle_timer(self):
        if not self.timer.is_running:
            self.timer.start()
            self.start_button.setText("Пауза")
            self.qt_timer.start(1000)
            self.progress_bar.setMaximum(self.timer.get_total_seconds())
            self.progress_bar.setValue(self.timer.get_seconds_left())
        else:
            self.timer.pause()
            self.start_button.setText("Старт")
            self.qt_timer.stop()
            self.progress_bar.setMaximum(self.timer.get_total_seconds())
            self.progress_bar.setValue(self.timer.get_total_seconds())

    def start_work(self):
        self.timer.reset_to_work()
        self.time_label.setText(self.timer.get_time_display())
        self.progress_bar.setMaximum(self.timer.get_total_seconds())
        self.progress_bar.setValue(self.timer.get_total_seconds())
        self.work_button.setEnabled(False)
        self.break_button.setEnabled(True)
        self.qt_timer.stop()
        self.start_button.setText("Старт")

    def start_break(self):
        self.timer.reset_to_break()
        self.time_label.setText(self.timer.get_time_display())
        self.progress_bar.setMaximum(self.timer.get_total_seconds())
        self.progress_bar.setValue(self.timer.get_total_seconds())
        self.work_button.setEnabled(True)
        self.break_button.setEnabled(False)
        self.qt_timer.stop()
        self.start_button.setText("Старт")

    def update_timer(self):
        if self.timer.update():
            self.time_label.setText(self.timer.get_time_display())
            self.progress_bar.setValue(self.timer.get_seconds_left())
        else:
            self.qt_timer.stop()
            self.timer.is_running = False
            self.start_button.setText("Старт")
            self.media.play_alarm()
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            self.setWindowFlags(Qt.WindowType.Widget)
            self.show()
            if self.timer.is_work_mode:
                self.start_break()
            else:
                self.start_work()

    def open_settings(self):
        dialog = SettingsDialog(self, self.media.image_dir, self.media.music_dir)
        if dialog.exec():
            settings = dialog.get_settings()
            self.media = MediaManager(settings["image_dir"], settings["music_dir"])
            self.update_background()
            # Восстановить видимость второстепенных кнопок после смены настроек
            for btn in self.secondary_buttons:
                btn.setVisible(self.menu_visible)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroApp()
    window.show()
    sys.exit(app.exec())