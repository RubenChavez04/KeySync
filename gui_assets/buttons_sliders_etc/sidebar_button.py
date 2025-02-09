from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import QToolButton


class SideBarToolButton(QToolButton):
    def __init__(self, parent=None, image_path=None, text=None, font_size=15, tooltip=None, width =200):
        super().__init__(parent)
        self.setFixedSize(width, 40)
        self.setStyleSheet("""
        QToolButton {
            Border-radius: 8px;
            background: #d9d9d9;
            color: black;
        }""")

        #added this to simplify adding images and button labels, one or the other for a cleaner look
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                icon = QPixmap(image_path)
                self.setIcon(QIcon(icon))
                self.setIconSize(icon.size())
            else:
                print("Failed to load image")
        else:
            self.setText(text)

        if tooltip:
            self.setToolTip(tooltip)
        if text:
            self.setText(text)
            self.setFont(QFont("Microsoft YaHei UI", font_size, QFont.Weight.Bold))