import pandas as pd

from tablecv import extract_table_from_ocr
from tablecv.utils.bounding_box import x_overlap_percentage
from tablecv.utils.table_extraction import row_data_to_dataframe


def test_extract_table_from_ocr_builds_dataframe_from_text_boxes():
    ocr_results = [
        ((0, 0, 10, 5), "Name"),
        ((20, 0, 10, 5), "Qty"),
        ((0, 20, 10, 5), "Tea"),
        ((20, 20, 10, 5), "2"),
        ((0, 40, 10, 5), "Coffee"),
        ((20, 40, 10, 5), "1"),
    ]

    dataframe = extract_table_from_ocr(ocr_results)

    pd.testing.assert_frame_equal(
        dataframe,
        pd.DataFrame([["Name", "Qty"], ["Tea", "2"], ["Coffee", "1"]]),
    )


def test_extract_table_from_ocr_returns_empty_dataframe_for_empty_input():
    dataframe = extract_table_from_ocr([])

    assert dataframe.empty


def test_extract_table_from_ocr_preserves_duplicate_box_text_in_public_api():
    ocr_results = [
        ((0, 0, 10, 5), "First"),
        ((0, 0, 10, 5), "Last"),
        ((20, 0, 10, 5), "Age"),
        ((0, 20, 10, 5), "Ada"),
        ((20, 20, 10, 5), "36"),
        ((0, 40, 10, 5), "Grace"),
        ((20, 40, 10, 5), "85"),
    ]

    dataframe = extract_table_from_ocr(ocr_results)

    assert dataframe.iat[0, 0] == "First Last"
    assert dataframe.iat[0, 1] == "Age"


def test_extract_table_from_ocr_handles_adjacent_columns_without_gap():
    ocr_results = [
        ((0, 0, 10, 5), "Name"),
        ((10, 0, 10, 5), "Qty"),
        ((0, 20, 10, 5), "Tea"),
        ((10, 20, 10, 5), "2"),
        ((0, 40, 10, 5), "Coffee"),
        ((10, 40, 10, 5), "1"),
    ]

    dataframe = extract_table_from_ocr(ocr_results)

    pd.testing.assert_frame_equal(
        dataframe,
        pd.DataFrame([["Name", "Qty"], ["Tea", "2"], ["Coffee", "1"]]),
    )


def test_row_data_to_dataframe_preserves_duplicate_box_text_order():
    box = (0, 0, 10, 5)
    rows = [[(0, box), (0, box)]]
    ocr_results = [(box, "John"), (box, "Doe")]

    dataframe = row_data_to_dataframe(rows, ocr_results, row_count=1, col_count=1)

    assert dataframe.iat[0, 0] == "John Doe"


def test_x_overlap_percentage_handles_zero_width_boxes():
    overlap = x_overlap_percentage((5, 0, 0, 10), (0, 10))

    assert overlap == 0
