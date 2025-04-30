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
        """
        :param text: The text to display in the marquee.
        :param parent: Parent QWidget (optional).
        :param scroll_speed: Speed of scrolling in milliseconds (lower is faster).
        :param pause_duration: Pause time (in milliseconds) at the beginning and at both ends.
        """
        super().__init__(parent)

        # Create the main scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setWidgetResizable(True)

        # Disable mouse events entirely (to prevent misalignment or unwanted behavior)
        self.scroll_area.setEnabled(False)

        # Create the label that holds the text
        self.text_label = QLabel(self)
        self.text_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.scroll_area.setWidget(self.text_label)

        # Set layout for the custom widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Scrolling parameters
        self.scroll_speed = scroll_speed  # Controls smoothness (lower is faster)
        self.pause_duration = pause_duration  # Pause duration in milliseconds
        self.timer = QTimer(self)  # Timer for scrolling
        self.offset = 0  # Tracks the current scroll position
        self.scroll_direction = 1  # 1 for forward, -1 for reverse
        self.is_paused = False  # Tracks if the marquee is currently paused

        # Set initial text
        self.setText(text)

    def setText(self, text):
        """Set the text on the label and prepare for scrolling."""
        self.text_label.setText(text)
        self.offset = 0  # Reset the offset
        self.scroll_direction = 1  # Reset the direction
        self.is_paused = True  # Indicate an initial pause

        # Adjust the label size based on its content
        metrics = QFontMetrics(self.text_label.font())
        text_width = metrics.horizontalAdvance(text)
        label_height = self.scroll_area.height()
        self.text_label.setFixedSize(text_width, label_height)

        # Stop any running timer
        self.stop_scrolling()

        # Decide if scrolling is necessary
        if text_width > self.scroll_area.width():
            # Start scroll after an initial pause
            QTimer.singleShot(self.pause_duration, self.start_scrolling)
        else:
            # No scrolling necessary; reset offset to 0
            self.text_label.setFixedSize(self.scroll_area.width(), label_height)

    def start_scrolling(self):
        """Start the scrolling animation."""
        self.is_paused = False  # Unpause
        if not self.timer.isActive():
            self.timer.timeout.connect(self.scroll_text)
            self.timer.start(self.scroll_speed)

    def stop_scrolling(self):
        """Stop the scrolling animation."""
        if self.timer.isActive():
            self.timer.stop()

    def scroll_text(self):
        """Scroll the text horizontally and pause at edges."""
        if self.is_paused:
            return  # Skip animation while paused

        # Get the horizontal scroll bar and its current value
        scrollbar = self.scroll_area.horizontalScrollBar()
        current_value = scrollbar.value()

        # Determine the new position
        step = 1  # Smooth scrolling (adjust for ultra-smoothness)
        new_value = current_value + (self.scroll_direction * step)

        # Handle direction reversal and pause at edges
        if new_value >= scrollbar.maximum():  # Reached the end
            self.scroll_direction = -1  # Reverse direction
            self.pause_at_edge(scrollbar.maximum())  # Pause at edge
        elif new_value <= scrollbar.minimum():  # Reached the start
            self.scroll_direction = 1  # Reverse direction
            self.pause_at_edge(scrollbar.minimum())  # Pause at edge
        else:
            scrollbar.setValue(new_value)

    def pause_at_edge(self, position):
        """Pause the scrolling for a specified duration at an edge."""
        self.is_paused = True  # Temporarily pause
        self.timer.stop()  # Stop scrolling during pause

        def resume_scrolling():
            self.scroll_area.horizontalScrollBar().setValue(position)  # Ensure it stays at the edge
            self.is_paused = False  # Resume scrolling
            self.timer.start(self.scroll_speed)  # Restart the timer

        QTimer.singleShot(self.pause_duration, resume_scrolling)

    def resizeEvent(self, event):
        """Ensure behavior remains consistent if the widget is resized."""
        # Re-check scrolling requirements on resize
        super().resizeEvent(event)
        self.setText(self.text_label.text())

