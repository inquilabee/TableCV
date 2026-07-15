from collections.abc import Sequence
from dataclasses import dataclass, field

from tablecv.types import BoundingBox, BoundingBoxTuple
from tablecv.utils.box_geometry import (
    box_to_coords as _box_to_coords,
)
from tablecv.utils.box_geometry import (
    filter_boxes as _filter_boxes,
)
from tablecv.utils.box_geometry import (
    table_bounding_box,
)
from tablecv.utils.box_geometry import (
    x_overlap_percentage as _x_overlap_percentage,
)
from tablecv.utils.cell_assignment import (
    cell_boundaries_along_x as _cell_boundaries_along_x,
)
from tablecv.utils.cell_assignment import (
    estimate_cell_numbers as _estimate_cell_numbers,
)
from tablecv.utils.row_detection import (
    RowCluster,
    estimate_reference_row,
    non_overlapping_boxes,
)
from tablecv.utils.row_detection import (
    estimate_rows as _estimate_rows,
)
from tablecv.utils.row_detection import (
    mode as _mode,
)
from tablecv.utils.table_region import (
    estimate_table_reference_row,
    select_table_rows,
    trim_rows_before_reference,
)

type BoundingBoxLike = BoundingBox | BoundingBoxTuple
type CellPosition = tuple[int, BoundingBoxTuple]


@dataclass(slots=True)
class TableLayout:
    source_boxes: list[BoundingBox]
    min_row: int = 3
    min_col: int = 2
    table_bounds: BoundingBox | None = None
    filtered_boxes: list[BoundingBox] = field(default_factory=list)
    rows: list[RowCluster] = field(default_factory=list)
    reference_row: RowCluster = field(default_factory=lambda: RowCluster([]))
    column_count: int = 0
    rows_with_cell_numbers: list[list[CellPosition]] = field(default_factory=list)

    @classmethod
    def from_boxes(cls, boxes: Sequence[BoundingBoxLike], min_row: int = 3, min_col: int = 2) -> "TableLayout":
        layout = cls(
            source_boxes=[BoundingBox.from_tuple(box) for box in boxes],
            min_row=min_row,
            min_col=min_col,
        )
        layout._infer()
        return layout

    @property
    def row_count(self) -> int:
        return len(self.rows_with_cell_numbers)

    def _infer(self) -> None:
        if not self.source_boxes:
            return

        table_rows = self._table_rows_from_source()
        self.reference_row, self.column_count = estimate_table_reference_row(
            table_rows,
            self.min_row,
            self.min_col,
        )
        table_rows = trim_rows_before_reference(table_rows, self.reference_row)
        self._update_table_bounds(table_rows)

        if self._has_reference_grid():
            cell_boundaries = _cell_boundaries_along_x(self.reference_row)
            self.rows_with_cell_numbers = _estimate_cell_numbers(table_rows, cell_boundaries)

    def _table_rows_from_source(self) -> list[RowCluster]:
        self.table_bounds = table_bounding_box(self.source_boxes)
        self.filtered_boxes = _filter_boxes(self.source_boxes, self.table_bounds, self.min_row, self.min_col)
        self.rows = _estimate_rows(non_overlapping_boxes(self.filtered_boxes))
        return select_table_rows(self.rows, self.min_row, self.min_col)

    def _update_table_bounds(self, table_rows: list[RowCluster]) -> None:
        if table_rows:
            self.table_bounds = table_bounding_box([box.as_tuple for row in table_rows for box in row.boxes])

    def _has_reference_grid(self) -> bool:
        return bool(self.reference_row.boxes) and self.column_count > 0


def box_to_coords(box: BoundingBoxLike) -> list[tuple[float, float]]:
    return _box_to_coords(box)


def get_non_overlapping_boxes(boxes: Sequence[BoundingBoxLike]) -> list[BoundingBoxTuple]:
    return [box.as_tuple for box in non_overlapping_boxes(boxes)]


def estimate_rows(boxes: Sequence[BoundingBoxLike]) -> list[list[BoundingBoxTuple]]:
    return [row.tuples for row in _estimate_rows(boxes)]


def estimate_reference_column(rows: Sequence[Sequence[BoundingBoxLike]]) -> tuple[list[BoundingBoxTuple], int]:
    reference_row, column_count = estimate_reference_row([RowCluster.from_boxes(row) for row in rows])
    return reference_row.tuples, column_count


def mode(values: list[int]) -> int:
    return _mode(values)


def cell_boundaries_along_x(reference_row: Sequence[BoundingBoxLike]) -> list[tuple[float, float]]:
    return _cell_boundaries_along_x(RowCluster.from_boxes(reference_row))


def x_overlap_percentage(box: BoundingBoxLike, bound: tuple[float, float]) -> float:
    return _x_overlap_percentage(box, bound)


def estimate_cell_numbers(
    rows: Sequence[Sequence[BoundingBoxLike]],
    cell_bounds: list[tuple[float, float]],
) -> list[list[CellPosition]]:
    return _estimate_cell_numbers([RowCluster.from_boxes(row) for row in rows], cell_bounds)


def get_rows_from_boxes(ocr_boxes: Sequence[BoundingBoxLike]) -> tuple[int, int, list[list[CellPosition]]]:
    """
    Given a list of boxes as ``(x, y, width, height)``, return row count,
    column count, and each box annotated with its estimated cell index.
    """
    layout = TableLayout.from_boxes(ocr_boxes)
    return layout.row_count, layout.column_count, layout.rows_with_cell_numbers


def get_table_bounding_box(boxes: Sequence[BoundingBoxLike]) -> BoundingBoxTuple:
    return table_bounding_box(boxes).as_tuple


def filter_boxes(
    boxes: Sequence[BoundingBoxLike],
    table: BoundingBoxLike,
    min_row: int = 3,
    min_col: int = 2,
) -> list[BoundingBoxTuple]:
    return [box.as_tuple for box in _filter_boxes(boxes, table, min_row, min_col)]
