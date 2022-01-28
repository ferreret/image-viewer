"""
QtImageViewer.py: PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
"""
import os
import sys
from typing import Optional, Any

import PySide6
from PySide6.QtCore import Signal, QRectF, QSizeF
from PySide6.QtGui import Qt, QPixmap, QImage, QPainterPath, QTransform, QBrush, QPen, QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QFileDialog, QGraphicsRectItem, \
    QGraphicsItem, QMessageBox

from components.resize_rect import ResizableRect

__author__ = "NBL"
__version__ = "1.0"


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class QtImageViewer(QGraphicsView):
    """
    PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.
    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)
    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = Signal(float, float)
    rightMouseButtonPressed = Signal(float, float)
    leftMouseButtonReleased = Signal(float, float)
    rightMouseButtonReleased = Signal(float, float)
    leftMouseButtonDoubleClicked = Signal(float, float)
    rightMouseButtonDoubleClicked = Signal(float, float)

    # Image viewer modes
    VIEWER_MODE, DESIGN_MODE = list(range(2))

    # ------------------------------------------------------------------------------------------------------------------
    # Constructor
    def __init__(self):
        super().__init__()

        # Image is displayed as QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        # noinspection PyUnresolvedReferences
        self.scene.selectionChanged.connect(self.selectionChanged)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction
        self.canZoom = True
        self.canPan = True

        # Image viewer mode
        self._mode = self.VIEWER_MODE

        # Utilizo este valor para puntero del rectangulo que está activo para crearlo
        self._current_rect_item = None
        self._start_point = None

    # --------------------------------------------------------------------------------------------------------------
    # Functions
    def hasImage(self) -> bool:
        """ Returns whether or not the scene contains an image pixmap."""
        return self._pixmapHandle is not None

    # --------------------------------------------------------------------------------------------------------------
    def clearImage(self) -> None:
        """ Removes the current image pixmap from the scene if it exists."""
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    # --------------------------------------------------------------------------------------------------------------
    def pixmap(self) -> Optional[Any]:
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists."""
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    # --------------------------------------------------------------------------------------------------------------
    def image(self) -> Optional[Any]:
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists."""
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    # --------------------------------------------------------------------------------------------------------------
    def setImage(self, image: Any) -> None:
        """
        Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")

        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)

        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    # --------------------------------------------------------------------------------------------------------------
    def updateViewer(self) -> None:
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return

        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], self.aspectRatioMode)  # Lo pongo en modo que conserve el aspect ratio
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    # Comento esta funcion porque me interesa sacar este diálogo fuera del visor
    # --------------------------------------------------------------------------------------------------------------
    def loadImageFromFile(self, fileName="") -> None:
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will pop up a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            fileName, _ = QFileDialog.getOpenFileName(self, "Open image file.")

        if len(fileName) and os.path.isfile(fileName):
            image = QImage(fileName)
            self.setImage(image)

    # --------------------------------------------------------------------------------------------------------------
    def setViewerMode(self):
        self._mode = self.VIEWER_MODE

    # --------------------------------------------------------------------------------------------------------------
    def setDesignMode(self):
        self._mode = self.DESIGN_MODE

    # --------------------------------------------------------------------------------------------------------------
    def deleteSelectedItems(self):
        """ Show a dialog to confirm deletion. """

        if len(self.scene.selectedItems()) == 0:
            return

        reply = QMessageBox.question(self, "Confirm Deletion", "Delete selected items?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsRectItem):
                self.scene.removeItem(item)

    # --------------------------------------------------------------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------------------------------------------------------------
    def selectionChanged(self):
        """ Slot creado para pintar de color diferente los elementos seleccionados """
        try:
            for item in self.scene.items():
                if isinstance(item, QGraphicsRectItem):
                    if item.isSelected():
                        item.setBrush(QBrush(QColor(255, 225, 98, 127)))
                    else:
                        item.setBrush(QBrush(QColor(255, 0, 0, 127)))
        except Exception as e:
            print("[ERROR] Error al cambiar el color de los elementos seleccionados")
            print(e)

    # ------------------------------------------------------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------------------------
    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        """
        Reimplemented from QWidget.
        Maintain current zoom on resize
        """
        self.updateViewer()

    # --------------------------------------------------------------------------------------------------------------

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """ Start mouse pan or zoom mode """
        scenePos = self.mapToScene(event.position().toPoint())

        if event.button() == Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            # noinspection PyUnresolvedReferences
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        else:
            if self._mode == self.VIEWER_MODE:
                """Comportamiento en el caso de que estamos en modo visualización"""
                if self.canPan:
                    self.setDragMode(QGraphicsView.ScrollHandDrag)
                # noinspection PyUnresolvedReferences
                self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())

            elif self._mode == self.DESIGN_MODE and self.hasImage():
                """Comportamiento en el caso de que estamos en modo diseño"""
                # print(self.scene.itemAt(scenePos, QTransform()).type())
                if self.scene.itemAt(scenePos, QTransform()) is not None \
                        and self.scene.itemAt(scenePos, QTransform()).type() == 7:
                    self._current_rect_item = ResizableRect()
                    self._current_rect_item.setBrush(QColor(255, 0, 0, 127))
                    pen = QPen(Qt.red)
                    pen.setCosmetic(True)
                    pen.setWidth(3)
                    self._current_rect_item.setPen(pen)
                    self._current_rect_item.setFlags(QGraphicsItem.ItemIsMovable
                                                     | QGraphicsItem.ItemIsSelectable)

                    self.scene.addItem(self._current_rect_item)
                    self._start_point = scenePos
                    print("Start point: ", self._start_point)
                    rect = QRectF(self._start_point, QSizeF(0, 0))
                    self._current_rect_item.setRect(rect)

        QGraphicsView.mousePressEvent(self, event)

    # --------------------------------------------------------------------------------------------------------------
    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        scenePos = self.mapToScene(event.position().toPoint())
        # print("Mouse move: ", scenePos, "Event: ", event.position().toPoint())
        if self._mode == self.DESIGN_MODE and self.hasImage():
            if self._current_rect_item is not None:
                if scenePos.x() < self._start_point.x() or scenePos.y() < self._start_point.y():
                    rectSize = QSizeF(0, 0)
                else:
                    rectSize = QSizeF(scenePos.x() - self._start_point.x(),
                                      scenePos.y() - self._start_point.y())
                rect = QRectF(self._start_point, rectSize)

                self._current_rect_item.setRect(rect)
        QGraphicsView.mouseMoveEvent(self, event)

    # --------------------------------------------------------------------------------------------------------------
    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """ End mouse pan or zoom mode """
        scenePos = self.mapToScene(event.position().toPoint())

        if event.button() == Qt.MouseButton.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QPainterPath())  # Clear current selection area
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QGraphicsView.NoDrag)
            # noinspection PyUnresolvedReferences
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        else:
            if self._mode == self.VIEWER_MODE:
                self.setDragMode(QGraphicsView.NoDrag)
                # noinspection PyUnresolvedReferences
                self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
            elif self._mode == self.DESIGN_MODE:
                self._current_rect_item = None

        QGraphicsView.mouseReleaseEvent(self, event)

    # --------------------------------------------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def mouseDoubleClickEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """ Show the entire image"""
        scenePos = self.mapToScene(event.position().toPoint())
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.RightButton:
            if self.canZoom:
                self.zoomStack.clear()
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())

        QGraphicsView.mouseDoubleClickEvent(self, event)

    # --------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("[INFO] Starting test main...")
    print(f"[INFO] Using PySide6 version: {PySide6.__version__}")


    def handleLeftClick(x, y):
        print(f"[INFO] Left click: ({x}, {y})")
        row = int(y)
        column = int(x)
        print(f"Clicked on image pixel: row = {row}, column = {column}")


    # Create the application
    app = QApplication(sys.argv)

    # Create image viewer and load an image file to display
    viewer = QtImageViewer()
    viewer.loadImageFromFile()

    # Handle left mouse clicks with custom slot
    # noinspection PyUnresolvedReferences
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    # Show the viewer and run application
    viewer.show()
    sys.exit(app.exec())
