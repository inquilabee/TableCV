import pandas as pd

from tablecv import extract_table_from_ocr
from tablecv.types import BoundingBox, TextBox
from tablecv.utils.bounding_box import TableLayout, estimate_reference_column, x_overlap_percentage
from tablecv.utils.table_extraction import TableExtractor, row_data_to_dataframe


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


def test_extract_table_from_ocr_detects_table_region_inside_document():
    ocr_results = [
        ((0, 0, 80, 8), "Invoice"),
        ((0, 12, 80, 8), "Brand"),
        ((0, 24, 80, 8), "Date: 2026-07-15"),
        ((0, 36, 80, 8), "Bill To"),
        ((0, 48, 80, 8), "Address"),
        ((0, 80, 70, 8), "Description"),
        ((100, 80, 35, 8), "Price"),
        ((160, 80, 25, 8), "Qty"),
        ((220, 80, 35, 8), "Total"),
        ((0, 96, 70, 8), "Tea"),
        ((100, 96, 35, 8), "$2"),
        ((160, 96, 25, 8), "3"),
        ((220, 96, 35, 8), "$6"),
        ((0, 112, 70, 8), "Coffee"),
        ((100, 112, 35, 8), "$5"),
        ((160, 112, 25, 8), "1"),
        ((220, 112, 35, 8), "$5"),
        ((0, 128, 70, 8), "Cake"),
        ((100, 128, 35, 8), "$4"),
        ((160, 128, 25, 8), "2"),
        ((220, 128, 35, 8), "$8"),
        ((0, 160, 80, 8), "Thank you"),
        ((180, 172, 75, 8), "Total: $19"),
    ]

    dataframe = extract_table_from_ocr(ocr_results)

    pd.testing.assert_frame_equal(
        dataframe,
        pd.DataFrame(
            [
                ["Description", "Price", "Qty", "Total"],
                ["Tea", "$2", "3", "$6"],
                ["Coffee", "$5", "1", "$5"],
                ["Cake", "$4", "2", "$8"],
            ]
        ),
    )


def test_extract_table_from_ocr_uses_table_header_when_body_rows_have_missing_cells():
    ocr_results = [
        ((0, 0, 80, 8), "Price List"),
        ((0, 16, 80, 8), "Interior Design"),
        ((0, 48, 70, 8), "Service"),
        ((120, 48, 35, 8), "Lite"),
        ((180, 48, 50, 8), "Normal"),
        ((260, 48, 35, 8), "Plus"),
        ((0, 64, 90, 8), "First Room"),
        ((120, 64, 35, 8), "$100"),
        ((260, 64, 35, 8), "$500"),
        ((0, 80, 110, 8), "Additional consultation"),
        ((180, 80, 20, 8), "2"),
        ((260, 80, 20, 8), "4"),
        ((0, 96, 80, 8), "Warranty"),
        ((120, 96, 20, 8), "No"),
        ((180, 96, 25, 8), "Yes"),
        ((0, 128, 120, 8), "Call for a quote"),
    ]

    dataframe = extract_table_from_ocr(ocr_results)

    pd.testing.assert_frame_equal(
        dataframe,
        pd.DataFrame(
            [
                ["Service", "Lite", "Normal", "Plus"],
                ["First Room", "$100", "", "$500"],
                ["Additional consultation", "", "2", "4"],
                ["Warranty", "No", "Yes", ""],
            ]
        ),
    )


def test_extract_table_from_ocr_ignores_single_box_noise_inside_table_region():
    ocr_results = [
        ((0, 0, 70, 8), "Description"),
        ((100, 0, 35, 8), "Price"),
        ((160, 0, 25, 8), "Qty"),
        ((220, 0, 35, 8), "Total"),
        ((0, 16, 70, 8), "Product 01"),
        ((100, 16, 35, 8), "$00"),
        ((160, 16, 25, 8), "1"),
        ((220, 16, 35, 8), "$00"),
        ((0, 32, 70, 8), "Product 02"),
        ((100, 32, 35, 8), "$00"),
        ((160, 32, 25, 8), "1"),
        ((220, 32, 35, 8), "$00"),
        ((-80, 40, 35, 8), "BILL"),
        ((0, 48, 70, 8), "Product 03"),
        ((100, 48, 35, 8), "$00"),
        ((160, 48, 25, 8), "1"),
        ((220, 48, 35, 8), "$00"),
        ((-80, 56, 20, 8), "TO"),
        ((0, 64, 70, 8), "Product 04"),
        ((100, 64, 35, 8), "$00"),
        ((160, 64, 25, 8), "1"),
        ((220, 64, 35, 8), "$00"),
    ]

    dataframe = extract_table_from_ocr(ocr_results)

    pd.testing.assert_frame_equal(
        dataframe,
        pd.DataFrame(
            [
                ["Description", "Price", "Qty", "Total"],
                ["Product 01", "$00", "1", "$00"],
                ["Product 02", "$00", "1", "$00"],
                ["Product 03", "$00", "1", "$00"],
                ["Product 04", "$00", "1", "$00"],
            ]
        ),
    )


def test_extract_table_from_ocr_excludes_multicell_metadata_before_table_header():
    ocr_results = [
        ((0, 0, 70, 8), "Bill To"),
        ((180, 0, 90, 8), "Invoice #123"),
        ((0, 16, 90, 8), "Ada Lovelace"),
        ((180, 16, 90, 8), "2026-07-15"),
        ((0, 32, 70, 8), "Description"),
        ((120, 32, 35, 8), "Qty"),
        ((220, 32, 35, 8), "Total"),
        ((0, 48, 70, 8), "Tea"),
        ((120, 48, 35, 8), "3"),
        ((220, 48, 35, 8), "$6"),
        ((0, 64, 70, 8), "Coffee"),
        ((120, 64, 35, 8), "1"),
        ((220, 64, 35, 8), "$5"),
        ((0, 80, 70, 8), "Cake"),
        ((120, 80, 35, 8), "2"),
        ((220, 80, 35, 8), "$8"),
    ]

    dataframe = extract_table_from_ocr(ocr_results)

    pd.testing.assert_frame_equal(
        dataframe,
        pd.DataFrame(
            [
                ["Description", "Qty", "Total"],
                ["Tea", "3", "$6"],
                ["Coffee", "1", "$5"],
                ["Cake", "2", "$8"],
            ]
        ),
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


def test_text_box_exposes_named_geometry_properties():
    text_box = TextBox.from_ocr_result(((5, 10, 20, 4), "Total"))

    assert text_box.x == 5
    assert text_box.y == 10
    assert text_box.width == 20
    assert text_box.height == 4
    assert text_box.text == "Total"


def test_bounding_box_handles_geometry_operations():
    outer = BoundingBox.from_tuple((0, 0, 30, 20))
    inner = BoundingBox.from_tuple((5, 5, 10, 5))

    assert outer.as_tuple == (0.0, 0.0, 30.0, 20.0)
    assert outer.coords == [(0.0, 0.0), (30.0, 0.0), (30.0, 20.0), (0.0, 20.0)]
    assert outer.contains(inner)
    assert inner.x_overlap_percentage((0, 15)) == 100


def test_table_layout_assigns_rows_and_columns():
    layout = TableLayout.from_boxes(
        [
            (0, 0, 10, 5),
            (20, 0, 10, 5),
            (0, 20, 10, 5),
            (20, 20, 10, 5),
            (0, 40, 10, 5),
            (20, 40, 10, 5),
        ]
    )

    assert layout.row_count == 3
    assert layout.column_count == 2
    assert layout.rows_with_cell_numbers[0] == [(0, (0, 0, 10, 5)), (1, (20, 0, 10, 5))]


def test_reference_column_tie_uses_first_seen_row_length():
    first_row = [(0, 0, 10, 5), (20, 0, 10, 5), (40, 0, 10, 5)]
    second_row = [(0, 20, 10, 5), (20, 20, 10, 5)]

    reference_row, column_count = estimate_reference_column([first_row, second_row])

    assert reference_row == first_row
    assert column_count == 3


def test_table_extractor_keeps_public_dataframe_behavior():
    extractor = TableExtractor.from_ocr_results(
        [
            ((0, 0, 10, 5), "Name"),
            ((20, 0, 10, 5), "Qty"),
            ((0, 20, 10, 5), "Tea"),
            ((20, 20, 10, 5), "2"),
            ((0, 40, 10, 5), "Coffee"),
            ((20, 40, 10, 5), "1"),
        ]
    )

    pd.testing.assert_frame_equal(
        extractor.to_dataframe(),
        pd.DataFrame([["Name", "Qty"], ["Tea", "2"], ["Coffee", "1"]]),
    )
