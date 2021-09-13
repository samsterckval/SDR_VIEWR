from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from settings import SdrSettings
try:
    from rtlsdr import RtlSdr
except Exception as e:
    import time
    print(f"rtlsdr not found : {e}")


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

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
            sdr_props = [p for p in dir(RtlSdr) if isinstance(getattr(RtlSdr, p), property)]
            # print(sdr_props)
            for key, val in self.sdr_settings.__dict__.items():
                if key in sdr_props:
                    setattr(sdr, key, val)

        while self._run_flag:

            if ok:
                samples = sdr.read_samples(self.sdr_settings.DEFAULT_READ_SIZE)
            else:
                x = np.linspace(-np.pi*self.sdr_settings.bandwidth//2,
                                np.pi*self.sdr_settings.bandwidth//2,
                                self.sdr_settings.DEFAULT_READ_SIZE)
                samples = np.sin(x*(self.sdr_settings.center_freq+np.random.randint(0, 10, 1)))*self.sdr_settings.gain

                time.sleep(0.1)

            # print(samples.shape)

            self.change_pixmap_signal.emit(samples)

        if ok:
            sdr.close()
            del sdr
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
