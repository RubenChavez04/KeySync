from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtWidgets import QToolButton


class SideBarToolButtonMini(QToolButton):
    def __init__(self, parent=None, image_path=None, text=None, tooltip=None, font_size=15, italic=False):
        super().__init__(parent)
        self.setFixedSize(95, 40)
        italic = "italic" if italic else "normal"
        self.setStyleSheet(f"""
        QToolButton {{
            Border-radius: 8px;
            background: #d9d9d9;
            color: black;
            font-style: {italic};
            }}
        QToolTip {{
            font: bold 14px;
            background-color: transparent;
            border-radius: 10px;
            }}
        """)
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
            self.setFont(QFont("Microsoft YaHei UI", font_size, QFont.Weight.Bold))

        if tooltip:
            self.setToolTip(tooltip)