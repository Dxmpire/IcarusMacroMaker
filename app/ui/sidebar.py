from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.btn_macros = QPushButton("Macros")
        self.btn_profiles = QPushButton("Profiles")
        self.btn_settings = QPushButton("Settings")
        self.btn_logs = QPushButton("Logs")

        layout.addWidget(self.btn_macros)
        layout.addWidget(self.btn_profiles)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_logs)
        layout.addStretch()

        self.setLayout(layout)
