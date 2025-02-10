from PyQt6.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout


class Page(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        frame = QFrame(self)
        frame.setFixedSize(800, 480)
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        frame.setStyleSheet("""
        QFrame {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #bfbfbf,
                stop: 1 #737373
            );
            border: 2px solid white
        }""")
        layout.addWidget(frame)
        self.setLayout(layout)