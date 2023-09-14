import pandas as pd

from tablecv.utils.bounding_box import get_rows_from_boxes


def row_data_to_dataframe(rows, ocr_results, row_count, col_count):
    ocr_dict = dict(ocr_results)

    text_data = [[[] for _ in range(col_count)] for _ in range(row_count)]

    for idx, row in enumerate(rows):
        for cell_num, cell_box in row:
            text = ocr_dict[cell_box]
            text_data[idx][cell_num].append(text)  # noqa

    data = [[None for _ in range(col_count)] for _ in range(row_count)]

    for row_idx, row in enumerate(text_data):
        for col_idx, cell in enumerate(row):
            text = " ".join(text_data[row_idx][col_idx])
            data[row_idx][col_idx] = text or ""  # noqa

    df = pd.DataFrame(data)

    return df


def extract_table_from_ocr(ocr_results: list[tuple[tuple[float, float, float, float], str]]) -> pd.DataFrame:
    boxes = [res[0] for res in ocr_results]

    row_count, col_count, rows = get_rows_from_boxes(boxes)

    dataframe = row_data_to_dataframe(rows, ocr_results, row_count, col_count)

    return dataframe
