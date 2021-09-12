from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
try:
    from rtlsdr import RtlSdr
except Exception as e:
    import time
    print(f"rtlsdr not found : {e}")


class SdrSettings:

    def __init__(self,
                 sample_rate: int = 24e5,
                 center_freq: int = 470625e3,
                 gain: int = 4,
                 bandwidth: int = 3000,
                 DEFAULT_READ_SIZE: int = 256*1024,
                 nfft: int = 1024):

        self.sample_rate = sample_rate
        self.center_freq = center_freq
        self.gain = gain
        self.bandwidth = bandwidth
        self.DEFAULT_READ_SIZE = DEFAULT_READ_SIZE
        self.nfft = nfft

    def __str__(self):
        return f"SDR Settings :\n" \
               f"--------------------\n" \
               f"sample rate : {self.sample_rate}\n" \
               f"center freq : {self.center_freq}\n" \
               f"gain        : {self.gain}\n" \
               f"bandwidth   : {self.bandwidth}\n" \
               f"read size   : {self.DEFAULT_READ_SIZE}\n" \
               f"nfft        : {self.nfft}\n"


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    change_settings_signal = pyqtSignal(SdrSettings)

    def __init__(self, sdr_settings: SdrSettings):
        super().__init__()
        self._run_flag = True

        self.sdr_settings: SdrSettings = sdr_settings

    def run(self):
        print(f"Running with settings : \n{self.sdr_settings}")
        ok = False
        try:
            sdr = RtlSdr()
            ok = True
        except Exception as e:
            print(f"Exception during radio opening : {e}")
            pass
        # configure device
        # sdr.sample_rate = self.sdr_settings.sample_rate
        # sdr.center_freq = self.sdr_settings.center_freq
        # sdr.gain = self.sdr_settings.gain
        # sdr.bandwidth = self.sdr_settings.bandwidth
        #
        # Below should be a shorter, cleaner and cooler version of the above
        if ok:
            for key, val in self.sdr_settings.__dict__.items():
                if key in sdr.__dict__.items():
                    setattr(sdr, key, val)

            while self._run_flag:
                samples = sdr.read_samples()
                self.change_pixmap_signal.emit(samples)

            sdr.close()
            del sdr
        else:
            while self._run_flag:
                x = np.linspace(-np.pi*10, np.pi*10, self.sdr_settings.DEFAULT_READ_SIZE)
                samples = np.sin(x*np.random.randint(0, 100, 1))
                self.change_pixmap_signal.emit(samples)
                time.sleep(0.3)

        print("Thread stopping")

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

    def restart(self, new_settings: SdrSettings = None):
        if new_settings is not None:
            self.sdr_settings = new_settings
        self._run_flag = False
        self.wait()
        self._run_flag = True
        self.start()
