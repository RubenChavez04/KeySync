from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout
import random

class Page(QWidget):
    def __init__(self, parent, image_path=None):
        random_hex1 = f"{random.randint(0x000000, 0xFFFFFF):06x}"
        random_hex2 = f"{random.randint(0x000000, 0xFFFFFF):06x}"
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        frame = QFrame(self)
        frame.setFixedSize(800, 480)
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if image_path:
            frame.setStyleSheet(f"""
                QFrame {{
                    background-image: url({image_path});
                    background-repeat: no-repeat;
                    background-position: center;
                    border: 2px solid darkgray;
            }}""")
        else: #default to static background
            frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #{random_hex1},
                    stop: 1 #{random_hex2}
                );
                border: 2px solid darkgray;
            }}""")
        layout.addWidget(frame)
        self.setLayout(layout)
