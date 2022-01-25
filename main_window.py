from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QMainWindow

import util

# TODO: Localización de los textos


# ----------------------------------------------------------------------------------------------------------------------
# Main Window
# Implementing designer funcionality
# ----------------------------------------------------------------------------------------------------------------------
from qtImageViewer import QtImageViewer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.viewer = None
        self.setWindowTitle("Form Designer")
        self.setMinimumSize(1280, 1024)

        self.create_menubar()
        self.create_statusbar()
        self.create_viewer()

    # ------------------------------------------------------------------------------------------------------------------
    # Create menu bar
    def create_menubar(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        # Add action to file menu
        open_file = QAction("Open File", self)
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)
        file_menu.addAction(open_file)

    # ------------------------------------------------------------------------------------------------------------------
    # Create status bar
    def create_statusbar(self):
        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------------------------------------------------------
    # Create viewer
    def create_viewer(self):
        self.viewer = QtImageViewer()
        self.viewer.keep_aspect_ratio = True

        self.viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.viewer.canPan = True
        self.viewer.canZoom = True

        self.setCentralWidget(self.viewer)

    # ------------------------------------------------------------------------------------------------------------------
    # Open image in designer
    def open_file(self):
        image, name = util.loadImageFromFile(self, "sample_images")

        if image is not None:
            self.viewer.setImage(image)
            self.statusBar().showMessage("Image loaded: " + name)

