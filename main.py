# import numpy as np
from PyQt5.QtWidgets import QApplication
from app import App
import sys


def _main(*args):

    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    _main('PyCharm')
