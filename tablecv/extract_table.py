import numpy as np
import pandas as pd
from paddleocr import PaddleOCR

from tablecv.utils.table_extraction import extract_table_from_ocr

paddle_ocr = PaddleOCR(use_angle_cls=True)


def text_box_from_ocr(image_path) -> list[tuple[tuple[float, float, float, float], str]]:
    """Given an image path, returns a list of tuple of box(x, y, w, h) and text"""

    def standardize_box(coords):
        a, _, c, _ = np.array(coords)
        x, y = a
        w, h = c - a

        return x, y, w, h

    result = paddle_ocr.ocr(image_path, cls=True)

    return [(standardize_box(box), text) for box, (text, _) in result[0]]


def extract_table(image_path) -> pd.DataFrame:
    ocr = text_box_from_ocr(image_path)
    return extract_table_from_ocr(ocr)


if __name__ == "__main__":
    img_path = r"/Users/dayhatt/workspace/projects/food_ocr/food_ocr/media/column_table2.png"
    print(extract_table(img_path))
