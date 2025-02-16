from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QToolButton, QSizePolicy


class ActionButton(QToolButton):
    def __init__(self, parent=None, text=None, tooltip=None, font_size=10):
        super().__init__(parent)
        self.setFixedSize(90, 40)
        self.setCheckable(True)
        self.setToolTip(tooltip)
        self.setText(text)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFont(QFont("Microsoft YaHei", font_size, QFont.Weight.Bold))
        self.setStyleSheet("""
            QToolButton {
                Border-radius: 8px;
                background: #999999;
                color: black;
                }
            QToolButton:checked {
                background-color: #d9d9d9;
                color: black;
                }
            QToolTip {
                font: bold 14px;
                background-color: transparent;
                border-radius: 10px;
                color: white;
                }

            """)
