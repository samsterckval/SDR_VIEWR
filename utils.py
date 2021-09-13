import io
import numpy as np
from matplotlib import figure
from typing import Tuple


def get_img_array(fig: figure, img_shape: Tuple[int, int]):
    buff = io.BytesIO()
    fig.savefig(buff, format='raw', facecolor='white', transparent=False)
    buff.seek(0)
    img_array = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    img_array = img_array.reshape((*img_shape, 4))
    buff.close()
    return img_array
