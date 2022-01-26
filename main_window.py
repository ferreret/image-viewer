from PySide6.QtGui import QAction, Qt, QActionGroup
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

        self.create_viewer()
        self.create_menubar()
        self.create_statusbar()

    # ------------------------------------------------------------------------------------------------------------------
    # Create menu bar
    def create_menubar(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        edit_menu = menu.addMenu("Edit")

        # Add action to file menu
        open_file = QAction("Open File", self)
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)
        file_menu.addAction(open_file)

        # Add QActionGroup to edit menu
        viewer_mode_normal = QAction("Normal", self)
        viewer_mode_normal.setCheckable(True)
        viewer_mode_normal.setChecked(True)
        viewer_mode_normal.triggered.connect(self.viewer.setViewerMode)
        viewer_mode_design = QAction("Design", self)
        viewer_mode_design.setCheckable(True)
        viewer_mode_design.triggered.connect(self.viewer.setDesignMode)
        edit_menu.addSeparator().setText("Viewer mode")
        edit_menu.addAction(viewer_mode_normal)
        viewer_mode_group = QActionGroup(self)
        viewer_mode_group.addAction(viewer_mode_normal)
        viewer_mode_group.addAction(viewer_mode_design)
        edit_menu.addAction(viewer_mode_normal)
        edit_menu.addAction(viewer_mode_design)

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

