import os
import re

from PyQt6.QtCore import QPoint, Qt, QSize
from PyQt6.QtGui import QMouseEvent, QPixmap, QIcon, QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QPushButton, QInputDialog, QFileDialog, QColorDialog, QGraphicsDropShadowEffect

from gui_assets.signal_dispatcher import global_signal_dispatcher

class ButtonWidget(QPushButton):
    """draggable button widget with custom sizing parameters, users can select button size"""
    def __init__(self, parent, cell_size, size_multiplier=(1, 1), position=None, color="#f0f0f0",label= "", image_path=None):
        #needed a size multiplier for determining col and row span [0] is col [1] is row
        super().__init__(parent)
        self.button_selected = None
        #define parent grid
        self.label = label
        self.parent = parent
        self.grid_size = cell_size
        self.size_multiplier = size_multiplier
        if size_multiplier == (1,1):
            self.setFixedSize(cell_size, cell_size)
        else:
            self.setFixedSize(cell_size * size_multiplier[0] + (size_multiplier[0]*13)-13, #width = 100 * (how much columns to take) + spacing
                              cell_size * size_multiplier[1] + (size_multiplier[1]*20)-20)
        self.width = cell_size * size_multiplier[0] + (size_multiplier[0]*13)-13
        self.height = cell_size * size_multiplier[1] + (size_multiplier[1]*20)-20
        self.startPos = None
        self.last_valid_position = position if position else QPoint(0, 0)
        self.move(self.last_valid_position)

        #set saved color on restore or use default if new
        self.color = color
        self.setStyleSheet(
            f"QPushButton {{border-radius: 8px;background-color: {self.color};border: None;}} QPushButton:hover {{ background-color: #cccccc;}}")
        #global_signal_dispatcher.selected_button.connect(self.selected_button)
        self.functions = {
            "On_Press":[],
            "On_Press_Release":[],
            "Long_Press":[],
            "Long_Press_Release":[]
        }

        #set button label on restore or empty if new
        self.setText(self.label)

        #set button icon
        self.image_path = image_path
        self.edit_icon(restore=True)

        global_signal_dispatcher.add_label_signal.connect(self.edit_button_text)
        global_signal_dispatcher.change_color_signal.connect(self.edit_color)
        global_signal_dispatcher.delete_button_signal.connect(self.delete_widget)
        global_signal_dispatcher.add_icon_signal.connect(self.edit_icon)
        global_signal_dispatcher.selected_button.connect(self.selected_button)



    def edit_color(self):
        if self.button_selected==self:
            color = QColorDialog.getColor(initial=QColor(255, 255, 255), title="Select Color")
            self.color = color.name()
            if color.isValid():
                print(f"Hex color code: {self.color}")
                self.setStyleSheet(
                    re.sub(r'background-color:.*?;', f'background-color: {self.color};', self.styleSheet()))

    def edit_button_text(self):
        if self.button_selected==self:
            print("Edit button called")
            # When add label is pressed allow user to input new label
            new_text, ok = QInputDialog.getText(self, "Edit Button Text", "Enter new text:")
            if ok and new_text:
                print(new_text)
                self.label = new_text
                self.setText(self.label)

    def edit_icon(self, restore=False):
        if self.button_selected == self or restore:
            if not restore:
                self.image_path = self.choose_icon()

            if self.image_path is not None:
                pixmap = QPixmap(self.image_path)
                if not pixmap.isNull():
                    # Create a rounded pixmap from the original pixmap
                    button_size = QSize(self.width, self.height)  # Match button size or adjust as needed
                    radius = 8  # Adjust the corner radius as required
                    rounded_pixmap = self.create_rounded_icon(pixmap, button_size, radius)

                    # Set the rounded pixmap as the icon
                    icon = QIcon(rounded_pixmap)
                    self.setIcon(icon)
                    self.setIconSize(button_size)
                else:
                    print("Failed to load image or no image path")

    def create_rounded_icon(self, pixmap: QPixmap, size: QSize, radius: int) -> QPixmap:
        """
        Create a QPixmap with rounded corners that fully covers the button.

        :param pixmap: Original pixmap to be rounded.
        :param size: Size of the resulting rendered pixmap.
        :param radius: Radius for rounded corners.
        :return: Rounded QPixmap that fully covers the button.
        """
        # create a transparent pixmap for the rounded icon
        rounded_pixmap = QPixmap(size)
        rounded_pixmap.fill(Qt.GlobalColor.transparent)  # Transparent background

        # scale the original pixmap to exactly match the button size (ignores aspect ratio)
        scaled_pixmap = pixmap.scaled(size, Qt.AspectRatioMode.IgnoreAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)

        # use QPainter to draw the rounded corner image
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # clip the drawing area to a rounded rectangle
        path = QPainterPath()
        rect_f = rounded_pixmap.rect().toRectF()  # converts QRect to QRectF
        path.addRoundedRect(rect_f, radius, radius)  # round the corners with the radius param
        painter.setClipPath(path)

        # draw the scaled pixmap over the clipped rounded rectangle
        painter.drawPixmap(0, 0, scaled_pixmap)

        painter.end()
        return rounded_pixmap

    def choose_icon(self):
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        # change "" to downloads_folder to open downloads
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", downloads_folder,
                                                   "Image Files (*.png *.jpg *.bmp);;All Files (*)")
        if file_path:
            return file_path

    def delete_widget(self):
        if self.button_selected==self:
            self.deleteLater()
            global_signal_dispatcher.remove_widget_signal.emit(self)

    def selected_button(self, button_selected):
        self.button_selected = button_selected

        if self.button_selected == self:
            # Set shadow effect for an external border
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setColor(QColor(0, 255, 42, 255))  # Border/Outline color
            shadow.setBlurRadius(30)  # Remove blur, make a solid border
            shadow.setOffset(0, 0)  # Center the border around the widget
            shadow.setXOffset(0)  # No offset along X-axis
            shadow.setYOffset(0)  # No offset along Y-axis

            self.setGraphicsEffect(shadow)  # Apply the effect
        else:
            # Remove shadow effect when deselected
            self.setGraphicsEffect(None)
        self.update()

    def mouseDoubleClickEvent(self,event):
        """Handle double-click to rename the tab."""
        if event.button() == Qt.MouseButton.LeftButton: #if left click twice
            self.button_selected = self
            global_signal_dispatcher.selected_button.emit(self)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """mouse event handling for initializing dragging the widget."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.pos() #get mouse position
            self.last_valid_position = self.pos()#save old position for invalid widget placement
        if event.button() == Qt.MouseButton.RightButton:
            print(self.appID)
            if self.appID is not None:
                global_signal_dispatcher.function_press.emit(self.appID, 1)

    def mouseMoveEvent(self, event: QMouseEvent):
        """mouse event handling for dragging the widget."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            new_pos = self.mapToParent(event.pos() - self.startPos) #calculate mouse position based on initial mouse position
            self.move(self.parent.get_snapped_position(new_pos, self.size_multiplier)) #get a snapped position relative to the mouse pos

    def mouseReleaseEvent(self, event: QMouseEvent):
        """mouse event handling for releasing the widget and saving its pos if valid"""
        if event.button() == Qt.MouseButton.LeftButton:
            #get the snapped position for widget
            snapped_pos = self.parent.get_snapped_position(self.pos(), self.size_multiplier)

            #temporarily remove old positions, so widget can be moved 1 col over if needed
            self.parent.remove_widget_position(self)

            #check if the snapped position is valid to prevent overlapping
            if self.parent.is_position_available(snapped_pos, self.size_multiplier): #if the position in grid is valid
                self.move(snapped_pos)  #move the widget to the snapped position
                self.parent.save_widget_position(self, snapped_pos)  #save the new position
                self.last_valid_position = snapped_pos  #update last valid position
            else: #if position is invalid revert to old position from press event
                self.parent.save_widget_position(self, self.last_valid_position)  #restore old position
                self.move(self.last_valid_position)  #revert to old position

