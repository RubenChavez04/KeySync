from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QLabel

class SideBarLabel(QWidget):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        label = QLabel(text, self)
        label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        label.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.Bold))