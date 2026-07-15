from collections.abc import Sequence

from tablecv.types import BoundingBox, BoundingBoxTuple

type BoundingBoxLike = BoundingBox | BoundingBoxTuple
type CellLimits = tuple[float, float, float]


def box_to_coords(box: BoundingBoxLike) -> list[tuple[float, float]]:
    return BoundingBox.from_tuple(box).coords


def table_bounding_box(boxes: Sequence[BoundingBoxLike]) -> BoundingBox:
    parsed_boxes = parse_boxes(boxes)
    min_x, min_y, max_x, max_y = box_extents(parsed_boxes)
    return BoundingBox(min_x, min_y, max_x - min_x, max_y - min_y)


def parse_boxes(boxes: Sequence[BoundingBoxLike]) -> list[BoundingBox]:
    return [BoundingBox.from_tuple(box) for box in boxes]


def box_extents(boxes: list[BoundingBox]) -> tuple[float, float, float, float]:
    return min_x(boxes), min_y(boxes), max_x(boxes), max_y(boxes)


def min_x(boxes: list[BoundingBox]) -> float:
    return min(box.x for box in boxes)


def min_y(boxes: list[BoundingBox]) -> float:
    return min(box.y for box in boxes)


def max_x(boxes: list[BoundingBox]) -> float:
    return max(box.max_x for box in boxes)


def max_y(boxes: list[BoundingBox]) -> float:
    return max(box.max_y for box in boxes)


def filter_boxes(
    boxes: Sequence[BoundingBoxLike],
    table: BoundingBoxLike,
    min_row: int = 3,
    min_col: int = 2,
) -> list[BoundingBox]:
    limits = table_cell_limits(BoundingBox.from_tuple(table), min_row, min_col)
    if limits is None:
        return []

    return [box for box in parse_boxes(boxes) if box_fits_cell_limits(box, limits)]


def table_cell_limits(table_box: BoundingBox, min_row: int, min_col: int) -> CellLimits | None:
    if table_box.width <= 0 or table_box.height <= 0:
        return None

    return (
        table_box.width / min_col,
        table_box.height / min_row,
        table_box.area / (min_row * min_col),
    )


def box_fits_cell_limits(box: BoundingBox, cell_limits: CellLimits) -> bool:
    max_cell_width, max_cell_height, max_cell_area = cell_limits
    return all(
        (
            is_within_cell_limit(box.width, max_cell_width),
            is_within_cell_limit(box.height, max_cell_height),
            is_within_cell_limit(box.area, max_cell_area),
        )
    )


def is_within_cell_limit(value: float, limit: float) -> bool:
    return 0 <= value <= limit


def x_overlap_percentage(box: BoundingBoxLike, bound: tuple[float, float]) -> float:
    return BoundingBox.from_tuple(box).x_overlap_percentage(bound)
