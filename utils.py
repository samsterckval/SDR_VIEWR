import io
import numpy as np
from matplotlib import figure
from typing import Tuple
import os
import tensorflow as tf
from tensorflow.keras.models import load_model


def get_img_array(fig: figure, img_shape: Tuple[int, int]):
    buff = io.BytesIO()
    fig.savefig(buff, format='raw', facecolor='white', transparent=False)
    buff.seek(0)
    img_array = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    img_array = img_array.reshape((*img_shape, 4))
    buff.close()
    return img_array


def get_model(path: str):
    if not os.path.isfile(path):
        print("Path is not a valid file, get rekt")
        return

    model: tf.keras.Model = load_model(path)

    return model


def norm_image_and_predict(img: np.ndarray, model: tf.keras.Model):
    if img.shape[0] > 10:
        img = np.expand_dims(img, axis=0)

    if len(img.shape) > 3:
        img = img[:, :, :, :3]

    norm_img = img/255.

    if len(norm_img.shape) != 4:
        print(f"Something went wrong : shape of input = {norm_img.shape}")

    pred = model.predict(norm_img)[0][0]
    return pred