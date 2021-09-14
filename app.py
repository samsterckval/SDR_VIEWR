from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QProgressBar
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSlot, Qt
import numpy as np
from framegrabber_thread import VideoThread
import matplotlib.pyplot as plt
from utils import get_img_array, get_model, norm_image_and_predict
from settings import SdrSettings
from matplotlib.mlab import psd


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("~ Edgise Live SDR ~")
        self.setMinimumWidth(900)

        self.sdr_settings = SdrSettings(load_from_file=True,
                                        filename="settings.json",
                                        img_size=(1000, 1000),
                                        axes_off=False,
                                        predict=False)

        if self.sdr_settings.predict:
            self.model = get_model("models/model_it1.h5")
        else:
            self.model = None

        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(*self.sdr_settings.img_size)

        self.update_button = QPushButton('Update')

        fixed_width_labels = 80
        self.nfft_label = QLabel('NFFT')
        self.nfft_label.setFixedWidth(fixed_width_labels)
        self.gain_label = QLabel('gain')
        self.gain_label.setFixedWidth(fixed_width_labels)
        self.bandwidth_label = QLabel('bandwidth')
        self.bandwidth_label.setFixedWidth(fixed_width_labels)
        self.read_label = QLabel('read size')
        self.read_label.setFixedWidth(fixed_width_labels)
        self.samplefreq_label = QLabel('sample freq')
        self.samplefreq_label.setFixedWidth(fixed_width_labels)
        self.centerfreq_label = QLabel('center freq')
        self.centerfreq_label.setFixedWidth(fixed_width_labels)

        self.pred_bar = QProgressBar()
        self.pred_bar.setValue(50)

        self.axesoff_label = QLabel(" ")
        self.axesoff_label.setFixedWidth(fixed_width_labels)
        self.axesoff_checkbox = QCheckBox("Axes off")
        self.axesoff_checkbox.setChecked(self.sdr_settings.axes_off)

        self.nfft_input = QLineEdit(str(self.sdr_settings.nfft))
        self.gain_input = QLineEdit(str(self.sdr_settings.gain))
        self.bandwidth_input = QLineEdit(str(self.sdr_settings.bandwidth))
        self.read_input = QLineEdit(str(self.sdr_settings.DEFAULT_READ_SIZE))
        self.samplefreq_input = QLineEdit(str(self.sdr_settings.sample_rate))
        self.centerfreq_input = QLineEdit(str(self.sdr_settings.center_freq))

        nfft_layout = QHBoxLayout()
        nfft_layout.addWidget(self.nfft_label)
        nfft_layout.addWidget(self.nfft_input)

        gain_layout = QHBoxLayout()
        gain_layout.addWidget(self.gain_label)
        gain_layout.addWidget(self.gain_input)

        bandwidth_layout = QHBoxLayout()
        bandwidth_layout.addWidget(self.bandwidth_label)
        bandwidth_layout.addWidget(self.bandwidth_input)

        read_layout = QHBoxLayout()
        read_layout.addWidget(self.read_label)
        read_layout.addWidget(self.read_input)

        sample_layout = QHBoxLayout()
        sample_layout.addWidget(self.samplefreq_label)
        sample_layout.addWidget(self.samplefreq_input)

        center_layout = QHBoxLayout()
        center_layout.addWidget(self.centerfreq_label)
        center_layout.addWidget(self.centerfreq_input)

        axesoff_layout = QHBoxLayout()
        axesoff_layout.addWidget(self.axesoff_label)
        axesoff_layout.addWidget(self.axesoff_checkbox)

        vbox_right = QVBoxLayout()
        vbox_right.addLayout(nfft_layout)
        vbox_right.addLayout(gain_layout)
        vbox_right.addLayout(bandwidth_layout)
        vbox_right.addLayout(sample_layout)
        vbox_right.addLayout(center_layout)
        vbox_right.addLayout(read_layout)
        vbox_right.addLayout(axesoff_layout)
        vbox_right.addWidget(self.update_button)

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(self.image_label)
        vbox_left.addWidget(self.pred_bar)

        # create a vertical box layout and add the two labels
        hbox = QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        # set the vbox layout as the widgets layout
        self.setLayout(hbox)

        # create the video capture thread
        self.thread = VideoThread(self.sdr_settings)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.update_button.clicked.connect(self.update_settings)
        # start the thread
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def update_settings(self):
        if self.gain_input.text() != "auto":
            self.sdr_settings.gain = int(self.gain_input.text())
        else:
            self.sdr_settings.gain = 'auto'

        self.sdr_settings.bandwidth = int(self.bandwidth_input.text())
        self.sdr_settings.sample_rate = int(self.samplefreq_input.text())
        self.sdr_settings.center_freq = int(self.centerfreq_input.text())
        self.sdr_settings.nfft = int(self.nfft_input.text())
        self.sdr_settings.DEFAULT_READ_SIZE = int(self.read_input.text())
        self.sdr_settings.axes_off = bool(self.axesoff_checkbox.isChecked())

        self.sdr_settings.save_to_file(create=True)

        self.thread.restart(self.sdr_settings)

    @pyqtSlot(np.ndarray)
    def update_image(self, samples):
        """Updates the image_label with a new opencv image"""

        fig, ax = plt.subplots(nrows=1,
                               ncols=1,
                               figsize=(self.sdr_settings.img_size[0] // 100, self.sdr_settings.img_size[1] // 100),
                               dpi=100)  # two axes on figure
        new_psd, new_freq = psd(samples,
                                NFFT=self.sdr_settings.nfft,
                                Fs=self.sdr_settings.sample_rate)

        new_freq += self.sdr_settings.center_freq

        # print(new_freq.shape)

        new_psd = new_psd - np.min(new_psd)

        xlim = [self.sdr_settings.center_freq - self.sdr_settings.bandwidth // 2,
                self.sdr_settings.center_freq + self.sdr_settings.bandwidth // 2]

        lower_index = np.argmax(new_freq > xlim[0])
        upper_index = np.argmax(new_freq > xlim[1])

        new_freq = new_freq[lower_index:upper_index]
        new_psd = new_psd[lower_index:upper_index]

        new_psd = new_psd - np.min(new_psd)

        ax.set_ylim([0, 0.0004])
        if self.sdr_settings.axes_off:
            ax.axis("off")
        ax.plot(new_psd, color="black")
        img = get_img_array(fig, img_shape=self.sdr_settings.img_size).copy()

        if self.sdr_settings.predict:
            pred = norm_image_and_predict(img, self.model)
            val = pred * 100
            if val > 30:
                self.pred_bar.set
            self.pred_bar.setValue(pred * 100)

        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)
        plt.close(fig)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(*self.sdr_settings.img_size, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
