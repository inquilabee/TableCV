from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tablecv import extract_table
from tablecv.extract_table import text_box_from_ocr

SIMPLE_TABLE_IMAGE = Path(__file__).parent / "fixtures" / "images" / "simple_table.png"
MAGNIFIC_IMAGES = [
    Path(__file__).parent / "fixtures" / "images" / "magnific" / "architect_invoice_template.jpg",
    Path(__file__).parent / "fixtures" / "images" / "magnific" / "flat_design_invoice.jpg",
    Path(__file__).parent / "fixtures" / "images" / "magnific" / "geometric_architecture_invoice.jpg",
    Path(__file__).parent / "fixtures" / "images" / "magnific" / "interior_design_price_list.jpg",
    Path(__file__).parent / "fixtures" / "images" / "magnific" / "invoice_template_design.jpg",
]


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


class ImageFixtureEngine:
    def __init__(self, expected_image_path):
        self.expected_image_path = Path(expected_image_path)

    def predict(self, input):
        image_path = Path(input)
        assert image_path == self.expected_image_path
        image_bytes = image_path.read_bytes()
        assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n") or image_bytes.startswith(b"\xff\xd8\xff")
        return [
            {
                "dt_polys": [
                    [(45, 35), (141, 35), (141, 63), (45, 63)],
                    [(285, 35), (357, 35), (357, 63), (285, 63)],
                    [(45, 80), (117, 80), (117, 108), (45, 108)],
                    [(305, 80), (329, 80), (329, 108), (305, 108)],
                    [(45, 125), (189, 125), (189, 153), (45, 153)],
                    [(305, 125), (329, 125), (329, 153), (305, 153)],
                ],
                "rec_texts": ["NAME", "QTY", "TEA", "2", "COFFEE", "1"],
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


@pytest.mark.parametrize("image_path", [SIMPLE_TABLE_IMAGE, *MAGNIFIC_IMAGES])
def test_extract_table_reads_real_image_path_with_injected_ocr_engine(image_path):
    dataframe = extract_table(image_path, ocr_engine=ImageFixtureEngine(image_path))

    pd.testing.assert_frame_equal(
        dataframe,
        pd.DataFrame([["NAME", "QTY"], ["TEA", "2"], ["COFFEE", "1"]]),
    )


@pytest.mark.parametrize("image_path", MAGNIFIC_IMAGES)
def test_downloaded_magnific_fixtures_are_real_jpegs(image_path):
    image_bytes = image_path.read_bytes()

    assert image_bytes.startswith(b"\xff\xd8\xff")
    assert len(image_bytes) > 10_000


@pytest.mark.integration
@pytest.mark.filterwarnings("ignore:No ccache found.*:UserWarning")
def test_extract_table_with_paddleocr_real_image_fixture():
    dataframe = extract_table(SIMPLE_TABLE_IMAGE)

    assert not dataframe.empty
