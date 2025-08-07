from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog, QLabel

class SettingsDialog(QDialog):
    def __init__(self, parent=None, image_dir="", music_dir=""):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.image_dir = image_dir
        self.music_dir = music_dir

        layout = QVBoxLayout()

        self.image_label = QLabel(f"Папка изображений: {self.image_dir or 'Не выбрана'}")
        self.image_button = QPushButton("Выбрать папку изображений")
        self.image_button.clicked.connect(self.choose_image_dir)

        self.music_label = QLabel(f"Папка музыки: {self.music_dir or 'Не выбрана'}")
        self.music_button = QPushButton("Выбрать папку музыки")
        self.music_button.clicked.connect(self.choose_music_dir)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)

        layout.addWidget(self.image_label)
        layout.addWidget(self.image_button)
        layout.addWidget(self.music_label)
        layout.addWidget(self.music_button)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def choose_image_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку с изображениями")
        if directory:
            self.image_label.setText(f"Папка изображений: {directory}")
            self.image_dir = directory

    def choose_music_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку с музыкой")
        if directory:
            self.music_label.setText(f"Папка музыки: {directory}")
            self.music_dir = directory

    def get_settings(self):
        return {"image_dir": self.image_dir, "music_dir": self.music_dir}