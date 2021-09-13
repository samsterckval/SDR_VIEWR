import os
import json
from typing import Tuple


class SdrSettings:

    def __init__(self,
                 sample_rate: int = 24e5,
                 center_freq: int = 470625e3,
                 gain: int = 4,
                 bandwidth: int = 3000,
                 DEFAULT_READ_SIZE: int = 256*1024,  # Yes I know PEP8 complains about this, but its an SDR setting
                 nfft: int = 1024,
                 load_from_file: bool = False,
                 filename: str = None,
                 img_size: Tuple[int, int] = (1000, 1000),
                 axes_off: bool = True,
                 predict: bool = True):

        self.load_from_file = load_from_file
        self.filename = filename

        self.sample_rate = sample_rate
        self.center_freq = center_freq
        self.gain = gain
        self.bandwidth = bandwidth
        self.DEFAULT_READ_SIZE = DEFAULT_READ_SIZE
        self.nfft = nfft
        self.img_size = img_size
        self.axes_off = axes_off
        self.predict = predict

        if self.load_from_file:
            if self.filename is None:
                print("I can't load from a file if you don't supply me a file, retard")
            elif not os.path.exists(self.filename) and not os.path.isfile(self.filename):
                print("This is not a file you retard")
            else:
                with open(self.filename) as f:
                    data: dict = json.load(f)

                    for key, val in data.items():
                        if key in self.__dict__.keys():
                            setattr(self, key, val)
                        else:
                            print(f"Found bad key : '{key}' - with value : {val}")

                print(f"Loaded settings from file.")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def save_to_file(self, create=False):
        if not self.load_from_file and not create or self.filename is None:
            print("get fucked")
            return

        with open(self.filename, 'w+') as f:
            f.write(self.to_json())

        print(f"Saved settings to file\n{self}")

    def __str__(self):
        lon_key: int = len(max(list(self.__dict__.keys()), key=len)) + 1
        vals = []
        for val in list(self.__dict__.values()):
            vals.append(str(val))
        lon_val: int = len(max(vals, key=len)) + 1
        # lon_line = lon_key + lon_val + len(" : ") + 1

        splitter = '+' + lon_key * '-' + '--+' + lon_val * '-' + '--+\n'

        outstr = "SDR Settings :\n"
        outstr += splitter

        for key, val in self.__dict__.items():
            outstr += f"| {key :>{lon_key}} | {str(val):<{lon_val}} |\n"
            outstr += splitter

        return outstr

