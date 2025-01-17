import os
import cv2
import config
import numpy as np
import pandas as pd

from random import randint
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.ticker import NullLocator
from matplotlib.figure import Figure

from .normalize import normalize
from .filters import LowPassFilter


class SpatialProjection():
    def __init__(
        self,
        img_dir: str,
        img_len: int,
        polyfit_degree: int = 0
    ):
        self.img_dir = img_dir
        self.img_len = img_len
        self.polyfit_degree = polyfit_degree

    @staticmethod
    def __write_image(
        img: np.ndarray,
        write_dir: str,
        plane: str,
        name: str
    ):
        path = os.path.join(write_dir, plane)
        if not os.path.exists(path):
            os.makedirs(path)
        cv2.imwrite(os.path.join(path, name + ".jpg"), img)

    def __get_preocessed_data(
        self,
        data: pd.Series
    ) -> np.ndarray:
        processed_data = data.to_numpy().ravel()

        if self.polyfit_degree == 0:
            # ... First few (10) datapoints contains filter artifacts
            processed_data = LowPassFilter.apply(processed_data)[10:]
        else:
            t = np.linspace(0, 1, processed_data.shape[0])
            f = np.poly1d(np.polyfit(t, processed_data, self.polyfit_degree))
            processed_data = f(t)

        return processed_data

    def __generate_projection_image(
        self,
        x: np.ndarray,
        y: np.ndarray
    ) -> np.ndarray:
        img_len_inch = self.img_len / 100.0  # 100 is the Figure DPI value
        fig = Figure(figsize=(img_len_inch, img_len_inch))
        width, height = fig.get_size_inches() * fig.get_dpi()

        canvas = FigureCanvas(fig)
        ax = fig.gca()
        ax.plot(x, y, "-k", linewidth=2)
        ax.axis("off")
        ax.xaxis.set_major_locator(NullLocator())
        ax.yaxis.set_major_locator(NullLocator())
        # fig.tight_layout()
        canvas.draw()

        image = np.frombuffer(canvas.tostring_rgb(), dtype="uint8")
        return image.reshape(int(height), int(width), 3)

    def get_projection_images(
        self,
        data: pd.DataFrame,
        subject: str,
        gesture: str,
        write_image: bool = False
    ) -> list[np.ndarray]:
        landmark = data.columns[0][:-1]
        name = str(randint(100000, 999999))
        write_dir = os.path.join(self.img_dir, subject, gesture, landmark)

        x = self.__get_preocessed_data(data.filter(regex="x"))
        y = self.__get_preocessed_data(data.filter(regex="y"))
        z = self.__get_preocessed_data(data.filter(regex="z"))

        img_xy = self.__generate_projection_image(x, y)
        img_yz = self.__generate_projection_image(y, z)
        img_zx = self.__generate_projection_image(z, x)

        if write_image == True:
            self.__write_image(img_xy, write_dir, "xy", name)
            self.__write_image(img_yz, write_dir, "yz", name)
            self.__write_image(img_zx, write_dir, "zx", name)

        return [img_xy, img_yz, img_zx]
