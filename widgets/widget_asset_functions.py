from PyQt6.QtCore import QSize, Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


def create_rounded_icon(pixmap: QPixmap, size: QSize, radius: int) -> QPixmap:
    """
    Create a QPixmap with rounded corners that fully covers the button.

    :param pixmap: Original pixmap to be rounded.
    :param size: Size of the resulting rendered pixmap.
    :param radius: Radius for rounded corners.
    :return: Rounded QPixmap that fully covers the button.
    """
    rounded_pixmap = QPixmap(size)
    rounded_pixmap.fill(Qt.GlobalColor.transparent)

    scaled_pixmap = pixmap.scaled(size, Qt.AspectRatioMode.IgnoreAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)

    painter = QPainter(rounded_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    path = QPainterPath()
    rect_f = QRectF(rounded_pixmap.rect())
    path.addRoundedRect(rect_f, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, scaled_pixmap)
    painter.end()

    return rounded_pixmap

def selected_button(put_self, button_selected):
    try:
        #needed to put this because ts would fuck up
        if put_self.button_selected is None:
            return
        put_self.button_selected = button_selected

        if put_self.button_selected == put_self:
            # Set shadow effect for an external border
            shadow = QGraphicsDropShadowEffect(put_self)
            shadow.setColor(QColor(0, 255, 42, 255))  # Border/Outline color
            shadow.setBlurRadius(30)  # Remove blur, make a solid border
            shadow.setOffset(0, 0)  # Center the border around the widget
            shadow.setXOffset(0)  # No offset along X-axis
            shadow.setYOffset(0)  # No offset along Y-axis

            put_self.setGraphicsEffect(shadow)  # Apply the effect
        else:
            # Remove shadow effect when deselected
            put_self.setGraphicsEffect(None)
        put_self.update()
    except Exception as e:
        print(f"Error selecting button: {e}")