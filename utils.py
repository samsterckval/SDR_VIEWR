import io
import numpy as np
from matplotlib import figure


def get_img_array(fig: figure, img_shape: tuple):
    buff = io.BytesIO()
    fig.savefig(buff, format='raw', facecolor='white', transparent=False)
    buff.seek(0)
    img_array = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    img_array = img_array.reshape((*img_shape, 4))
    buff.close()
    return img_array
