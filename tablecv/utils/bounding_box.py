from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field

from tablecv.types import BoundingBox, BoundingBoxTuple

type BoundingBoxLike = BoundingBox | BoundingBoxTuple
type CellPosition = tuple[int, BoundingBoxTuple]


@dataclass(frozen=True, slots=True)
class RowCluster:
    boxes: list[BoundingBox]

    @classmethod
    def from_boxes(cls, boxes: Sequence[BoundingBoxLike]) -> "RowCluster":
        return cls(boxes=sorted((BoundingBox.from_tuple(box) for box in boxes), key=lambda box: box.x))

    @property
    def length(self) -> int:
        return len(self.boxes)

    @property
    def tuples(self) -> list[BoundingBoxTuple]:
        return [box.as_tuple for box in self.boxes]


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

        self.table_bounds = self._table_bounding_box(self.source_boxes)
        self.filtered_boxes = self._filter_boxes(self.source_boxes, self.table_bounds)
        non_overlap_boxes = self._non_overlapping_boxes(self.filtered_boxes)
        self.rows = self._estimate_rows(non_overlap_boxes)
        self.reference_row, self.column_count = self._estimate_reference_row(self.rows)

        if not self.reference_row.boxes or self.column_count == 0:
            return

        cell_boundaries = self._cell_boundaries_along_x(self.reference_row)
        self.rows_with_cell_numbers = self._estimate_cell_numbers(self.rows, cell_boundaries)

    @staticmethod
    def _non_overlapping_boxes(boxes: Sequence[BoundingBoxLike]) -> list[BoundingBox]:
        sorted_boxes = sorted((BoundingBox.from_tuple(box) for box in boxes), key=lambda box: box.area, reverse=True)
        non_overlapping_boxes = []

        while sorted_boxes:
            candidate = sorted_boxes.pop(0)
            is_inside_other_box = any(box.contains(candidate) for box in sorted_boxes)

            if not is_inside_other_box:
                non_overlapping_boxes.append(candidate)

        return non_overlapping_boxes

    @classmethod
    def _estimate_rows(cls, boxes: Sequence[BoundingBoxLike]) -> list[RowCluster]:
        sorted_boxes = sorted(cls._non_overlapping_boxes(boxes), key=lambda box: (box.y, box.x))
        rows = []

        while sorted_boxes:
            first_box = sorted_boxes.pop(0)
            row_boxes = [first_box]
            same_row_boxes = [box for box in sorted_boxes if first_box.y <= box.y <= first_box.y + first_box.height / 2]

            row_boxes.extend(same_row_boxes)
            for box in same_row_boxes:
                sorted_boxes.remove(box)

            rows.append(RowCluster.from_boxes(row_boxes))

        return rows

    @staticmethod
    def _estimate_reference_row(rows: list[RowCluster]) -> tuple[RowCluster, int]:
        if not rows:
            return RowCluster([]), 0

        row_lengths = [row.length for row in rows]
        most_common_length = Counter(row_lengths).most_common(1)[0][0]
        reference_rows = [row for row in rows if row.length == most_common_length]
        return reference_rows[0], most_common_length

    @staticmethod
    def _cell_boundaries_along_x(reference_row: RowCluster) -> list[tuple[float, float]]:
        return [(box.x + 0.5, box.max_x - 0.5) for box in reference_row.boxes]

    @staticmethod
    def _estimate_cell_numbers(
        rows: list[RowCluster],
        cell_bounds: list[tuple[float, float]],
    ) -> list[list[CellPosition]]:
        if not cell_bounds:
            return []

        result_rows = []
        min_bound_x = cell_bounds[0][0]
        max_bound_x = cell_bounds[-1][1]

        for row in rows:
            result_row = []

            for box in row.boxes:
                if box.x < min_bound_x:
                    cell_number = 0
                elif box.x >= max_bound_x:
                    cell_number = len(cell_bounds) - 1
                else:
                    _, cell_number = max(
                        ((box.x_overlap_percentage(bound), idx) for idx, bound in enumerate(cell_bounds)),
                        key=lambda item: item[0],
                    )

                result_row.append((cell_number, box.as_tuple))

            result_rows.append(result_row)

        return result_rows

    @staticmethod
    def _table_bounding_box(boxes: Sequence[BoundingBoxLike]) -> BoundingBox:
        parsed_boxes = [BoundingBox.from_tuple(box) for box in boxes]
        min_x = min(box.x for box in parsed_boxes)
        min_y = min(box.y for box in parsed_boxes)
        max_x = max(box.max_x for box in parsed_boxes)
        max_y = max(box.max_y for box in parsed_boxes)
        return BoundingBox(min_x, min_y, max_x - min_x, max_y - min_y)

    def _filter_boxes(self, boxes: Sequence[BoundingBoxLike], table: BoundingBoxLike) -> list[BoundingBox]:
        table_box = BoundingBox.from_tuple(table)
        if table_box.width <= 0 or table_box.height <= 0:
            return []

        max_cell_width = table_box.width / self.min_col
        max_cell_height = table_box.height / self.min_row
        max_cell_area = table_box.area / (self.min_row * self.min_col)

        return [
            box
            for box in (BoundingBox.from_tuple(box) for box in boxes)
            if 0 <= box.width <= max_cell_width
            and 0 <= box.height <= max_cell_height
            and 0 <= box.area <= max_cell_area
        ]


def box_to_coords(box: BoundingBoxLike) -> list[tuple[float, float]]:
    return BoundingBox.from_tuple(box).coords


def get_non_overlapping_boxes(boxes: Sequence[BoundingBoxLike]) -> list[BoundingBoxTuple]:
    return [box.as_tuple for box in TableLayout._non_overlapping_boxes(boxes)]


def estimate_rows(boxes: Sequence[BoundingBoxLike]) -> list[list[BoundingBoxTuple]]:
    return [row.tuples for row in TableLayout._estimate_rows(boxes)]


def mode(values: list[int]) -> int:
    return Counter(values).most_common(1)[0][0]


def estimate_reference_column(rows: Sequence[Sequence[BoundingBoxLike]]) -> tuple[list[BoundingBoxTuple], int]:
    reference_row, column_count = TableLayout._estimate_reference_row([RowCluster.from_boxes(row) for row in rows])
    return reference_row.tuples, column_count


def cell_boundaries_along_x(reference_row: Sequence[BoundingBoxLike]) -> list[tuple[float, float]]:
    return TableLayout._cell_boundaries_along_x(RowCluster.from_boxes(reference_row))


def x_overlap_percentage(box: BoundingBoxLike, bound: tuple[float, float]) -> float:
    return BoundingBox.from_tuple(box).x_overlap_percentage(bound)


def estimate_cell_numbers(
    rows: Sequence[Sequence[BoundingBoxLike]],
    cell_bounds: list[tuple[float, float]],
) -> list[list[CellPosition]]:
    return TableLayout._estimate_cell_numbers([RowCluster.from_boxes(row) for row in rows], cell_bounds)


def get_rows_from_boxes(ocr_boxes: Sequence[BoundingBoxLike]) -> tuple[int, int, list[list[CellPosition]]]:
    """
    Given a list of boxes as ``(x, y, width, height)``, return row count,
    column count, and each box annotated with its estimated cell index.
    """
    layout = TableLayout.from_boxes(ocr_boxes)
    return layout.row_count, layout.column_count, layout.rows_with_cell_numbers


def get_table_bounding_box(boxes: Sequence[BoundingBoxLike]) -> BoundingBoxTuple:
    return TableLayout._table_bounding_box(boxes).as_tuple


def filter_boxes(
    boxes: Sequence[BoundingBoxLike],
    table: BoundingBoxLike,
    min_row: int = 3,
    min_col: int = 2,
) -> list[BoundingBoxTuple]:
    return [box.as_tuple for box in TableLayout([], min_row=min_row, min_col=min_col)._filter_boxes(boxes, table)]
