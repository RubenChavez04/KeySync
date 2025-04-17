from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QPainterPath
from PyQt6.QtWidgets import QPushButton

from pi_code.signal_dispatcher_pi import pi_signal_dispatcher

class ClientButtonWidget(QPushButton):
    """
    Simplified client-side button widget that displays an icon, color, and text.
    Drag-and-edit functions have been removed.
    """

    def __init__(self, parent, cell_size, size_multiplier=(1, 1), position=None, color="#f0f0f0", label="",
                 image_path=None):
        super().__init__(parent)

        # Initialize size and position
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier
        self.width = cell_size * size_multiplier[0] + (size_multiplier[0] * 13) - 13
        self.height = cell_size * size_multiplier[1] + (size_multiplier[1] * 20) - 20
        self.setFixedSize(self.width, self.height)

        # Initialize attributes
        self.color = color
        self.label = label
        self.image_path = image_path
        self.functions = {
            "On_Press":[],
            "On_Press_Release":[],
            "Long_Press":[],
            "Long_Press_Release":[]
        }

        # Apply properties
        self.setStyleSheet(f"QPushButton {{border-radius: 8px; background-color: {self.color}; border: None;}}")
        self.setText(self.label)
        self.edit_icon()

    def edit_icon(self):
        """
        Sets the button icon using the provided image path. Icons are displayed with rounded corners.
        """
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
        """
        Create a QPixmap with rounded corners.

        :param pixmap: Original pixmap to be rounded.
        :param size: Size of the resulting pixmap.
        :param radius: Radius for rounded corners.
        :return: Rounded QPixmap.
        """
        #create a transparent pixmap for the rounded icon
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
                self.print_function(func)
        elif event.button() == Qt.MouseButton.RightButton:
            print("Button pressed: Long_Press functions triggered")
            for func in self.functions["Long_Press"]:
                self.print_function(func)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """handle button release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            print("Button released: On_Press_Release functions triggered")
            for func in self.functions["On_Press_Release"]:
                self.print_function(func)
        elif event.button() == Qt.MouseButton.RightButton:
            print("Button released: Long_Press_Release functions triggered")
            for func in self.functions["Long_Press_Release"]:
                self.print_function(func)
        super().mouseReleaseEvent(event)

    def print_function(self, func):
        """send signal for button press to client, or run locally depending on func"""
        colon_start = func.find(":")
        func_type = func[0:colon_start]
        param = func[colon_start+1:]
        print(func_type)
        print(param)
        print(f"Triggered function:{func}")
        if func_type == "Change Page":
            index = int(param)
            pi_signal_dispatcher.change_page_signal.emit(index)
            return
        else:
            pi_signal_dispatcher.send_func_signal.emit(func) #maybe do send_message(func) on the pi (have to import the client.py)
            return




