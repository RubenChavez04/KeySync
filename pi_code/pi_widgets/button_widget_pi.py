from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QPainterPath
from PyQt6.QtWidgets import QPushButton

from pi_code.signal_dispatcher_pi import pi_signal_dispatcher

class ClientButtonWidget(QPushButton):
    def __init__(self, parent, cell_size, size_multiplier=(1, 1), position=None, color="#f0f0f0", label="",
                 image_path=None):
        super().__init__(parent)
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier
        self.width = cell_size * size_multiplier[0] + (size_multiplier[0] * 13) - 13
        self.height = cell_size * size_multiplier[1] + (size_multiplier[1] * 20) - 20
        self.setFixedSize(self.width, self.height)

        self.color = color
        self.label = label
        self.image_path = image_path
        self.functions = {
            "On_Press":[],
            "On_Press_Release":[],
            "Long_Press":[],
            "Long_Press_Release":[]
        }
        self.setStyleSheet(f"QPushButton {{border-radius: 8px; background-color: {self.color}; border: None;}}")
        self.setText(self.label)
        self.edit_icon()

    def edit_icon(self):
        if self.image_path:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # Create a rounded pixmap from the original pixmap
                button_size = QSize(self.width, self.height)
                radius = 8
                rounded_pixmap = self.create_rounded_icon(pixmap, button_size, radius)

                # Set the rounded pixmap as the icon
                icon = QIcon(rounded_pixmap)
                self.setIcon(icon)
                self.setIconSize(button_size)

    def create_rounded_icon(self, pixmap: QPixmap, size: QSize, radius: int) -> QPixmap:
        rounded_pixmap = QPixmap(size)  #create a pixmap
        rounded_pixmap.fill(Qt.GlobalColor.transparent) #fill empty space with transparent color

        #scale the pixmap to fit the target size while ignoring aspect ratio
        scaled_pixmap = pixmap.scaled(size, Qt.AspectRatioMode.IgnoreAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)

        #use QPainter to draw the rounded corner image
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        #draw a rounded rectangle clipping path
        path = QPainterPath()   #create a clipping path
        rect_f = rounded_pixmap.rect().toRectF()
        path.addRoundedRect(rect_f, radius, radius)
        painter.setClipPath(path)

        #draw the scaled pixmap over the rounded rectangle
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()

        return rounded_pixmap

    def mousePressEvent(self, event):
        """handle button press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            print("Button pressed: On_Press functions triggered")

            for func in self.functions["On_Press"]:
                self.func_handler(func)
        elif event.button() == Qt.MouseButton.RightButton:
            print("Button pressed: Long_Press functions triggered")
            for func in self.functions["Long_Press"]:
                self.func_handler(func)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """handle button release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            print("Button released: On_Press_Release functions triggered")
            for func in self.functions["On_Press_Release"]:
                self.func_handler(func)
        elif event.button() == Qt.MouseButton.RightButton:
            print("Button released: Long_Press_Release functions triggered")
            for func in self.functions["Long_Press_Release"]:
                self.func_handler(func)
        super().mouseReleaseEvent(event)

    def delete(self):
        self.deleteLater()

    def func_handler(self, func):
        """send signal for button press to client, or run locally depending on func"""
        colon_start = func.split(":")
        func_type = colon_start[0]
        print(func_type)
        print(f"Triggered function:{func}")
        if func_type == "Change Page":
            page_name = colon_start[1]
            pi_signal_dispatcher.change_page_signal.emit(page_name)
            return
        else:
            pi_signal_dispatcher.send_func_signal.emit(func)
            return



"""
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("Button pressed: On_Press functions triggered")
            
            for func in self.functions["On_Press"]:
                self.func_handler(func)
        elif event.button() == Qt.MouseButton.RightButton:
            print("Button pressed: Long_Press functions triggered")
            for func in self.functions["Long_Press"]:
                self.func_handler(func)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("Button released: On_Press_Release functions triggered")
            for func in self.functions["On_Press_Release"]:
                self.func_handler(func)
        elif event.button() == Qt.MouseButton.RightButton:
            print("Button released: Long_Press_Release functions triggered")
            for func in self.functions["Long_Press_Release"]:
                self.func_handler(func)
        super().mouseReleaseEvent(event)
"""
