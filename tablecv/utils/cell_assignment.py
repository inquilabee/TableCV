from tablecv.types import BoundingBox
from tablecv.utils.row_detection import RowCluster

type CellPosition = tuple[int, tuple[float, float, float, float]]


def cell_boundaries_along_x(reference_row: RowCluster) -> list[tuple[float, float]]:
    return [(box.x + 0.5, box.max_x - 0.5) for box in reference_row.boxes]


def estimate_cell_numbers(
    rows: list[RowCluster],
    cell_bounds: list[tuple[float, float]],
) -> list[list[CellPosition]]:
    if not cell_bounds:
        return []

    return [[cell_position_for_box(box, cell_bounds) for box in row.boxes] for row in rows]


def cell_position_for_box(box: BoundingBox, cell_bounds: list[tuple[float, float]]) -> CellPosition:
    min_bound_x = cell_bounds[0][0]
    max_bound_x = cell_bounds[-1][1]

    if box.x < min_bound_x:
        return 0, box.as_tuple
    if box.x >= max_bound_x:
        return len(cell_bounds) - 1, box.as_tuple

    return best_cell_position_for_box(box, cell_bounds), box.as_tuple


def best_cell_position_for_box(box: BoundingBox, cell_bounds: list[tuple[float, float]]) -> int:
    _, cell_number = max(
        ((box.x_overlap_percentage(bound), idx) for idx, bound in enumerate(cell_bounds)),
        key=lambda item: item[0],
    )
    return cell_number
