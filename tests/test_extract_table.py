import numpy as np

from tablecv.extract_table import text_box_from_ocr


class LegacyPaddleEngine:
    def ocr(self, image_path, cls=True):
        assert image_path == "receipt.png"
        assert cls is True
        return [
            [
                (
                    [(0, 0), (10, 0), (10, 5), (0, 5)],
                    ("Tea", 0.98),
                )
            ]
        ]


class PredictPaddleEngine:
    def predict(self, input):
        assert input == "receipt.png"
        return [
            {
                "dt_polys": [[(0, 0), (10, 0), (10, 5), (0, 5)]],
                "rec_texts": ["Tea"],
            }
        ]


class NumpyPredictPaddleEngine:
    def predict(self, input):
        assert input == "receipt.png"
        return [
            {
                "dt_polys": np.array([[(0, 0), (10, 0), (10, 5), (0, 5)]]),
                "rec_texts": np.array(["Tea"]),
            }
        ]


def test_text_box_from_ocr_supports_legacy_paddle_ocr_shape():
    results = text_box_from_ocr("receipt.png", ocr_engine=LegacyPaddleEngine())

    assert results == [((0.0, 0.0, 10.0, 5.0), "Tea")]


def test_text_box_from_ocr_supports_predict_result_shape():
    results = text_box_from_ocr("receipt.png", ocr_engine=PredictPaddleEngine())

    assert results == [((0.0, 0.0, 10.0, 5.0), "Tea")]


def test_text_box_from_ocr_supports_numpy_predict_result_fields():
    results = text_box_from_ocr("receipt.png", ocr_engine=NumpyPredictPaddleEngine())

    assert results == [((0.0, 0.0, 10.0, 5.0), "Tea")]
