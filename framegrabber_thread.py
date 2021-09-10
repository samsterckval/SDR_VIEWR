from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from rtlsdr import *


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

        self.sample_rate = 24e5
        self.center_freq = 470625e3
        self.gain = 4
        self.bandwidth = 3000

    def run(self):
        sdr = RtlSdr()
        # configure device
        sdr.sample_rate = self.sample_rate
        sdr.center_freq = self.center_freq
        sdr.gain = self.gain
        sdr.bandwidth = self.bandwidth

        while self._run_flag:
            samples = sdr.read_samples(1024*256)
            self.change_pixmap_signal.emit(samples)

        sdr.close()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

    def restart(self):
        self._run_flag = False
        self.wait()
