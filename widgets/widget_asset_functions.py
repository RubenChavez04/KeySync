from PyQt6.QtCore import QSize, Qt, QRectF, QTimer, QPropertyAnimation, pyqtSlot, QEvent
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont, QFontMetrics, QTextDocument, \
    QAbstractTextDocumentLayout, QPalette
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QScrollArea, QWidget


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

def create_drop_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(13)
    shadow.setOffset(1, 1)
    shadow.setColor(QColor(0, 0, 0, 200))
    return shadow

class MarqueeLabel(QWidget):
    def __init__(self, text, parent=None, scroll_speed=60, pause_duration=3000):
        super().__init__(parent)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setEnabled(False)

        self.text_label = QLabel(self)
        self.text_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.scroll_area.setWidget(self.text_label)

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.scroll_speed = scroll_speed
        self.pause_duration = pause_duration
        self.timer = QTimer(self)
        self.offset = 0
        self.scroll_direction = 1
        self.is_paused = False

        self._is_deleting = False  # Flag to track if the widget is being deleted
        self.setText(text)

    def setText(self, text):
        self.text_label.setText(text)
        self.offset = 0
        self.scroll_direction = 1
        self.is_paused = True

        metrics = QFontMetrics(self.text_label.font())
        text_width = metrics.horizontalAdvance(text)
        label_height = self.scroll_area.height()

        self.text_label.setFixedSize(text_width, label_height)
        self.stop_scrolling()

        if text_width > self.scroll_area.width():
            QTimer.singleShot(self.pause_duration, self.start_scrolling)
        else:
            self.text_label.setFixedSize(self.scroll_area.width(), label_height)

    def start_scrolling(self):
        self.is_paused = False
        if not self.timer.isActive():
            self.timer.timeout.connect(self.scroll_text)
            self.timer.start(self.scroll_speed)

    def stop_scrolling(self):
        if self.timer.isActive():
            self.timer.stop()

    def scroll_text(self):
        if self.is_paused or self._is_deleting:  # Do not scroll if paused or deleting
            return

        scrollbar = self.scroll_area.horizontalScrollBar()
        current_value = scrollbar.value()
        step = 1
        new_value = current_value + (self.scroll_direction * step)

        if new_value >= scrollbar.maximum():
            self.scroll_direction = -1
            self.pause_at_edge(scrollbar.maximum())
        elif new_value <= scrollbar.minimum():
            self.scroll_direction = 1
            self.pause_at_edge(scrollbar.minimum())
        else:
            scrollbar.setValue(new_value)

    def pause_at_edge(self, position):
        self.is_paused = True
        self.timer.stop()

        def resume_scrolling():
            # Ensure the widget (self.scroll_area) is still valid
            if self._is_deleting or not self or not self.scroll_area:
                return  # Exit if the widget is deleting or invalid
            self.scroll_area.horizontalScrollBar().setValue(position)
            self.is_paused = False
            self.timer.start(self.scroll_speed)

        # Use self as the parent of QTimer
        QTimer.singleShot(self.pause_duration, resume_scrolling)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setText(self.text_label.text())

    def deleteLater(self):
        """Clean up timers and resources before deletion."""
        self._is_deleting = True  # Set the deleting flag
        self.stop_scrolling()  # Stop the timer
        if self.timer.isActive():
            self.timer.timeout.disconnect()  # Disconnect the timer (avoid further calls)
        super().deleteLater()
