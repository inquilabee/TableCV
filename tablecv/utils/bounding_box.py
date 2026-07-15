from collections import Counter

from shapely.geometry import Polygon

from tablecv.types import BoundingBox


def box_to_coords(box: BoundingBox) -> list[tuple[float, float]]:
    x, y, width, height = box
    return [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]


def get_non_overlapping_boxes(boxes: list[BoundingBox]) -> list[BoundingBox]:
    def box_overlap(box1: BoundingBox, box2: BoundingBox) -> bool:
        polygon1 = Polygon(box_to_coords(box1))
        polygon2 = Polygon(box_to_coords(box2))
        return polygon1.contains(polygon2)

    sorted_boxes = sorted(boxes, key=lambda box: box[2] * box[3], reverse=True)
    non_overlapping_boxes = []

    while sorted_boxes:
        first_item = sorted_boxes.pop(0)
        is_inside_other_polygon = any(box_overlap(box, first_item) for box in sorted_boxes)

        if not is_inside_other_polygon:
            non_overlapping_boxes.append(first_item)

    return non_overlapping_boxes


def estimate_rows(boxes: list[BoundingBox]) -> list[list[BoundingBox]]:
    sorted_boxes = sorted(get_non_overlapping_boxes(boxes), key=lambda box: (box[1], box[0]))
    rows = []

    while sorted_boxes:
        first_item = sorted_boxes.pop(0)
        row = [first_item]
        same_row_boxes = [box for box in sorted_boxes if first_item[1] <= box[1] <= first_item[1] + first_item[3] / 2]

        row.extend(same_row_boxes)
        for box in same_row_boxes:
            sorted_boxes.remove(box)

        row.sort(key=lambda box: box[0])
        rows.append(row)

    return rows


def mode(values: list[int]) -> int:
    return Counter(values).most_common(1)[0][0]


def estimate_reference_column(rows: list[list[BoundingBox]]) -> tuple[list[BoundingBox], int]:
    if not rows:
        return [], 0

    row_lengths = [len(row) for row in rows]
    most_freq = mode(row_lengths)
    reference_rows = [row for row in rows if len(row) == most_freq]
    return reference_rows[0], most_freq


def cell_boundaries_along_x(reference_row: list[BoundingBox]) -> list[tuple[float, float]]:
    return [(x + 0.5, x + width - 0.5) for x, _, width, _ in reference_row]


def x_overlap_percentage(box: BoundingBox, bound: tuple[float, float]) -> float:
    x, _, width, _ = box
    if width <= 0:
        return 0

    min_x, max_x = bound
    intersection = max(0, min(x + width, max_x) - max(x, min_x))
    return (intersection / width) * 100


def estimate_cell_numbers(
    rows: list[list[BoundingBox]],
    cell_bounds: list[tuple[float, float]],
) -> list[list[tuple[int, BoundingBox]]]:
    if not cell_bounds:
        return []

    result_rows = []
    min_bound_x = cell_bounds[0][0]
    max_bound_x = cell_bounds[-1][1]

    for row in rows:
        result_row = []

        for box in row:
            x, _, _, _ = box

            if x < min_bound_x:
                cell_number = 0
            elif x >= max_bound_x:
                cell_number = len(cell_bounds) - 1
            else:
                _, cell_number = max(
                    ((x_overlap_percentage(box, bound), idx) for idx, bound in enumerate(cell_bounds)),
                    key=lambda item: item[0],
                )

            result_row.append((cell_number, box))

        result_rows.append(result_row)

    return result_rows


def get_rows_from_boxes(ocr_boxes: list[BoundingBox]) -> tuple[int, int, list[list[tuple[int, BoundingBox]]]]:
    """
    Given a list of boxes as ``(x, y, width, height)``, return row count,
    column count, and each box annotated with its estimated cell index.
    """
    if not ocr_boxes:
        return 0, 0, []

    table = get_table_bounding_box(ocr_boxes)
    filtered_boxes = filter_boxes(ocr_boxes, table)
    non_overlap_boxes = get_non_overlapping_boxes(filtered_boxes)
    row_values = estimate_rows(non_overlap_boxes)
    reference_row, num_cols = estimate_reference_column(row_values)

    if not reference_row or num_cols == 0:
        return 0, 0, []

    cell_boundaries = cell_boundaries_along_x(reference_row)
    rows_with_cell_numbers = estimate_cell_numbers(row_values, cell_boundaries)
    return len(rows_with_cell_numbers), num_cols, rows_with_cell_numbers


def get_table_bounding_box(boxes: list[BoundingBox]) -> BoundingBox:
    min_x = min(box[0] for box in boxes)
    min_y = min(box[1] for box in boxes)
    max_x = max(box[0] + box[2] for box in boxes)
    max_y = max(box[1] + box[3] for box in boxes)

    return min_x, min_y, max_x - min_x, max_y - min_y


def filter_boxes(boxes: list[BoundingBox], table: BoundingBox, min_row: int = 3, min_col: int = 2) -> list[BoundingBox]:
    _, _, table_width, table_height = table
    if table_width <= 0 or table_height <= 0:
        return []

    max_cell_width = table_width / min_col
    max_cell_height = table_height / min_row
    max_cell_area = (table_width * table_height) / (min_row * min_col)

    return [
        box
        for box in boxes
        if 0 <= box[2] <= max_cell_width and 0 <= box[3] <= max_cell_height and 0 <= box[2] * box[3] <= max_cell_area
    ]
