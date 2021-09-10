from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSlot, Qt
import numpy as np
from framegrabber_thread import VideoThread
import matplotlib.pyplot as plt
from utils import get_img_array


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('FFT')

        self.nfft_input = QLineEdit("1024")
        self.fs_input = QLineEdit("30000")
        self.fc_input = QLineEdit("470625000")

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.textLabel)
        vbox.addWidget(self.nfft_input)
        vbox.addWidget(self.fs_input)
        vbox.addWidget(self.fc_input)

        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, samples):
        """Updates the image_label with a new opencv image"""

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10), dpi=100)  # two axes on figure
        new_psd, new_freq = plt.psd(samples,
                                    NFFT=int(self.nfft_input.text()),
                                    Fs=int(self.fs_input.text()),
                                    Fc=int(self.fc_input.text()),
                                    color="black")

        ax.axis("off")
        ax.plot(new_freq, new_psd, color="black")
        img = get_img_array(fig, img_shape=(1000, 1000)).copy()

        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)