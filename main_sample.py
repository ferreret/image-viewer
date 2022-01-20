import argparse
import sys

from PySide6.QtGui import Qt, QImage
from PySide6.QtWidgets import QApplication

from qtImageViewer import QtImageViewer


# Custom slot for handling mouse clicks in our viewer.
# Just prints the (row, column) matrix index of the
# image pixel that was clicked on.
def handleLeftClick(x, y):
    row = int(y)
    column = int(x)
    print(f"Pixel (row={row}, column={column})")


if __name__ == "__main__":
    # Paso por línea de comandos la imagen a mostrar
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="Path to the image", default="sample_images/mandala.jpg")
    args = vars(ap.parse_args())

    # Create the QApplication
    app = QApplication(sys.argv)

    # Create the image viewer
    viewer = QtImageViewer()

    # Set viewer's aspect ratio mode.
    # !!! ONLY applies to full image view.
    # !!! Aspect ratio always ignored when zoomed.
    #   Qt.IgnoreAspectRatio: Fit to viewport.
    #   Qt.KeepAspectRatio: Fit in viewport using aspect ratio.
    #   Qt.KeepAspectRatioByExpanding: Fill viewport using aspect ratio.
    viewer.aspectRatioMode = Qt.KeepAspectRatio

    # Set the viewer's scroll bar behaviour.
    #   Qt.ScrollBarAlwaysOff: Never show scroll bar.
    #   Qt.ScrollBarAlwaysOn: Always show scroll bar.
    #   Qt.ScrollBarAsNeeded: Show scroll bar only when zoomed.
    viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # Allow zooming with right mouse button.
    # Drag for zoom box, doubleclick to view full image.
    viewer.canZoom = True

    # Allow panning with left mouse button.
    viewer.canPan = True

    fileName = args["image"]
    image = QImage(fileName)

    # Display the image in the viewer
    viewer.setImage(image)

    # Handle left mouse clicks with your own custom slot
    # handleLeftClick(x, y). (x, y) are image coordinates.
    # For (row, col) matrix indexing, row=y and col=x.
    # ImageViewerQt also provides similar signals for
    # left/right mouse button press, release and doubleclick.
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    # Show the viewer and run the application
    viewer.show()
    sys.exit(app.exec())
