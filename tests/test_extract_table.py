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
KIRANA_INVOICE_IMAGES = [
    Path(__file__).parent / "fixtures" / "images" / "kirana" / "kirana_invoice_1.png",
    Path(__file__).parent / "fixtures" / "images" / "kirana" / "kirana_invoice_2.png",
    Path(__file__).parent / "fixtures" / "images" / "kirana" / "kirana_invoice_3.png",
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


class StaticImageFixtureEngine:
    def __init__(self, expected_image_path, dt_polys, rec_texts):
        self.expected_image_path = Path(expected_image_path)
        self.dt_polys = dt_polys
        self.rec_texts = rec_texts

    def predict(self, input):
        image_path = Path(input)
        assert image_path == self.expected_image_path
        image_bytes = image_path.read_bytes()
        assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n") or image_bytes.startswith(b"\xff\xd8\xff")
        return [
            {
                "dt_polys": self.dt_polys,
                "rec_texts": self.rec_texts,
            }
        ]


def _poly(x, y, width, height):
    return [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]


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


@pytest.mark.parametrize(
    ("image_path", "dt_polys", "rec_texts", "expected"),
    [
        (
            KIRANA_INVOICE_IMAGES[0],
            [
                _poly(30, 55, 120, 16),
                _poly(30, 88, 22, 14),
                _poly(75, 88, 170, 14),
                _poly(285, 88, 35, 14),
                _poly(340, 88, 40, 14),
                _poly(420, 88, 40, 14),
                _poly(470, 88, 55, 14),
                _poly(30, 108, 22, 14),
                _poly(75, 108, 170, 14),
                _poly(285, 108, 35, 14),
                _poly(340, 108, 40, 14),
                _poly(420, 108, 40, 14),
                _poly(470, 108, 55, 14),
                _poly(30, 128, 22, 14),
                _poly(75, 128, 170, 14),
                _poly(285, 128, 35, 14),
                _poly(340, 128, 40, 14),
                _poly(420, 128, 40, 14),
                _poly(470, 128, 55, 14),
                _poly(420, 202, 75, 14),
                _poly(520, 202, 70, 14),
            ],
            [
                "Invoice No: BILL/2024-25/48285",
                "S.N",
                "Item",
                "Qty",
                "Rate",
                "GST",
                "Total",
                "1",
                "PRS SOAP 75",
                "28",
                "188",
                "18%",
                "6228",
                "2",
                "BOURBON 150G",
                "49",
                "432",
                "18%",
                "24990",
                "TOTAL",
                "45226.44",
            ],
            pd.DataFrame(
                [
                    ["S.N", "Item", "Qty", "Rate", "GST", "Total"],
                    ["1", "PRS SOAP 75", "28", "188", "18%", "6228"],
                    ["2", "BOURBON 150G", "49", "432", "18%", "24990"],
                ]
            ),
        ),
        (
            KIRANA_INVOICE_IMAGES[1],
            [
                _poly(35, 58, 90, 12),
                _poly(160, 58, 130, 12),
                _poly(35, 130, 24, 13),
                _poly(75, 130, 190, 13),
                _poly(320, 130, 35, 13),
                _poly(395, 130, 45, 13),
                _poly(485, 130, 40, 13),
                _poly(585, 130, 70, 13),
                _poly(35, 150, 24, 13),
                _poly(75, 150, 190, 13),
                _poly(320, 150, 35, 13),
                _poly(395, 150, 45, 13),
                _poly(485, 150, 40, 13),
                _poly(585, 150, 70, 13),
                _poly(35, 170, 24, 13),
                _poly(75, 170, 190, 13),
                _poly(320, 170, 35, 13),
                _poly(395, 170, 45, 13),
                _poly(485, 170, 40, 13),
                _poly(585, 170, 70, 13),
                _poly(35, 338, 115, 13),
                _poly(620, 338, 75, 13),
            ],
            [
                "Invoice No:",
                "INV/2025-26/16003",
                "S.N",
                "Item Name",
                "Qty",
                "Rate",
                "Tax%",
                "Amount",
                "1",
                "SENSODY 70G",
                "22",
                "211.28",
                "18%",
                "7977.92",
                "2",
                "LX SOAP 150",
                "22",
                "288.61",
                "18%",
                "12918.71",
                "Grand Total",
                "101544.34",
            ],
            pd.DataFrame(
                [
                    ["S.N", "Item Name", "Qty", "Rate", "Tax%", "Amount"],
                    ["1", "SENSODY 70G", "22", "211.28", "18%", "7977.92"],
                    ["2", "LX SOAP 150", "22", "288.61", "18%", "12918.71"],
                ]
            ),
        ),
        (
            KIRANA_INVOICE_IMAGES[2],
            [
                _poly(30, 55, 130, 16),
                _poly(30, 88, 22, 14),
                _poly(75, 88, 170, 14),
                _poly(285, 88, 35, 14),
                _poly(340, 88, 40, 14),
                _poly(420, 88, 40, 14),
                _poly(470, 88, 55, 14),
                _poly(30, 108, 22, 14),
                _poly(75, 108, 170, 14),
                _poly(285, 108, 35, 14),
                _poly(340, 108, 40, 14),
                _poly(420, 108, 40, 14),
                _poly(470, 108, 55, 14),
                _poly(30, 128, 22, 14),
                _poly(75, 128, 170, 14),
                _poly(285, 128, 35, 14),
                _poly(340, 128, 40, 14),
                _poly(420, 128, 40, 14),
                _poly(470, 128, 55, 14),
                _poly(420, 210, 75, 14),
                _poly(520, 210, 70, 14),
            ],
            [
                "Invoice No: BILL/2024-25/97185",
                "S.N",
                "Item",
                "Qty",
                "Rate",
                "GST",
                "Total",
                "1",
                "ANNAPURNA 1KG",
                "44",
                "389",
                "5%",
                "17966",
                "2",
                "Parle Monaco Salted Biscuit 75",
                "42",
                "413",
                "18%",
                "20447",
                "TOTAL",
                "61014.94",
            ],
            pd.DataFrame(
                [
                    ["S.N", "Item", "Qty", "Rate", "GST", "Total"],
                    ["1", "ANNAPURNA 1KG", "44", "389", "5%", "17966"],
                    ["2", "Parle Monaco Salted Biscuit 75", "42", "413", "18%", "20447"],
                ]
            ),
        ),
    ],
)
def test_extract_table_reads_kirana_invoice_fixtures_with_injected_ocr_engine(
    image_path,
    dt_polys,
    rec_texts,
    expected,
):
    dataframe = extract_table(
        image_path,
        ocr_engine=StaticImageFixtureEngine(image_path, dt_polys, rec_texts),
    )

    pd.testing.assert_frame_equal(dataframe, expected)


@pytest.mark.parametrize("image_path", MAGNIFIC_IMAGES)
def test_downloaded_magnific_fixtures_are_real_jpegs(image_path):
    image_bytes = image_path.read_bytes()

    assert image_bytes.startswith(b"\xff\xd8\xff")
    assert len(image_bytes) > 10_000


@pytest.mark.parametrize("image_path", KIRANA_INVOICE_IMAGES)
def test_downloaded_kirana_invoice_fixtures_are_real_pngs(image_path):
    image_bytes = image_path.read_bytes()

    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(image_bytes) > 10_000


@pytest.mark.integration
@pytest.mark.filterwarnings("ignore:No ccache found.*:UserWarning")
def test_extract_table_with_paddleocr_real_image_fixture():
    dataframe = extract_table(SIMPLE_TABLE_IMAGE)

    assert not dataframe.empty
