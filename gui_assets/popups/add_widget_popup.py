from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton


class AddWidgetPopup(QDialog):
    """Popup window to select widget type"""
    def __init__(self, parent, deck):
        super().__init__(parent)
        self.setWindowTitle("Add Widget")
        self.setFixedSize(200, 150)
        self.deck = deck

        layout = QVBoxLayout()
        for text, size in [("1x1 Button", (1, 1)), ("2x2 Button", (2, 2)), ("Spotify Widget (2x4)", (4, 2))]:
            btn = QPushButton(text, self)
            btn.clicked.connect(lambda _, t=text, s=size: self.add_widget(t, s))
            layout.addWidget(btn)

        self.setLayout(layout)

    def add_widget(self, widget_type, size_multiplier):
        """Add a widget to the grid"""
        self.deck.add_widget(widget_type, size_multiplier)
        self.close()