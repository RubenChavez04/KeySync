from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

class ShadowFX(QGraphicsDropShadowEffect):
    def __init__(self, parent, color = (QColor(0,0,0,150))):
        super().__init__(parent)
        self.setBlurRadius(15)
        self.setOffset(0)
        self.setColor(color)