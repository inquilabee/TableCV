from collections import Counter, defaultdict, deque
from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd

from tablecv.types import BoundingBoxTuple, OCRResult, TextBox
from tablecv.utils.bounding_box import CellPosition, TableLayout


@dataclass(frozen=True, slots=True)
class TableRows:
    rows: Sequence[Sequence[CellPosition]]
    text_boxes: Sequence[TextBox]
    row_count: int
    column_count: int

    def to_dataframe(self) -> pd.DataFrame:
        ocr_text_by_box = defaultdict(deque)
        for text_box in self.text_boxes:
            ocr_text_by_box[text_box.bounds].append(text_box.text)

        row_box_counts = Counter(cell_box for row in self.rows for _, cell_box in row)
        text_data = [[[] for _ in range(self.column_count)] for _ in range(self.row_count)]

        for row_index, row in enumerate(self.rows):
            for cell_number, cell_box in row:
                if cell_number >= self.column_count:
                    continue

                texts = ocr_text_by_box[cell_box]
                if row_box_counts[cell_box] == 1:
                    text_data[row_index][cell_number].extend(texts)
                    texts.clear()
                elif texts:
                    text_data[row_index][cell_number].append(texts.popleft())

        data = [[" ".join(cell_texts) for cell_texts in row] for row in text_data]
        return pd.DataFrame(data)


@dataclass(frozen=True, slots=True)
class TableExtractor:
    text_boxes: Sequence[TextBox]

    @classmethod
    def from_ocr_results(cls, ocr_results: Sequence[OCRResult]) -> "TableExtractor":
        return cls(text_boxes=[TextBox.from_ocr_result(result) for result in ocr_results])

    @property
    def boxes(self) -> list[BoundingBoxTuple]:
        return [text_box.bounds for text_box in self.text_boxes]

    def to_dataframe(self) -> pd.DataFrame:
        if not self.text_boxes:
            return pd.DataFrame()

        layout = TableLayout.from_boxes(self.boxes)
        if layout.row_count == 0 or layout.column_count == 0:
            return pd.DataFrame()

        return TableRows(
            rows=layout.rows_with_cell_numbers,
            text_boxes=self.text_boxes,
            row_count=layout.row_count,
            column_count=layout.column_count,
        ).to_dataframe()


def row_data_to_dataframe(
    rows: Sequence[Sequence[CellPosition]],
    ocr_results: Sequence[OCRResult],
    row_count: int,
    col_count: int,
) -> pd.DataFrame:
    return TableRows(
        rows=rows,
        text_boxes=[TextBox.from_ocr_result(result) for result in ocr_results],
        row_count=row_count,
        column_count=col_count,
    ).to_dataframe()


def extract_table_from_ocr(ocr_results: Sequence[OCRResult]) -> pd.DataFrame:
    return TableExtractor.from_ocr_results(ocr_results).to_dataframe()
