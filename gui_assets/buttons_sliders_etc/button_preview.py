from PyQt6.QtWidgets import QPushButton


class ButtonPreview(QPushButton):
    def __init__(self, parent=None):
        super().__init__("Preview Button", parent)
        self.setCheckable(True)  # To allow "On/Off" state toggle
        self.setFixedSize(200, 200)
        self.update_style("Off")
        self.non_clickable = True

    def update_style(self, state):
        # Update button style based on state
        colors = {
            "On": "background-color: #4CAF50; color: white;",
            "Off": "background-color: #f44336; color: white;"
        }
        self.setStyleSheet(f"""
            QPushButton {{{
                colors[state]
            }}}
            QPushButton:hover{{
                background-color: {colors[state]};
            }}
            QPushButton:focus{{ 
                outline: none;
            }}
        """)
    def mousePressEvent(self, event):
        if not self.non_clickable:
            super().mousePressEvent(event)
        else:
            event.ignore()
    def set_clickable(self, clickable:bool):
        self.non_clickable = not clickable