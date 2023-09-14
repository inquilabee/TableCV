from collections import Counter

from shapely.geometry import Polygon


def box_to_coords(box):
    x, y, w, h = box
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def get_non_overlapping_boxes(boxes):
    def box_overlap(box1, box2):
        polygon1 = Polygon(box_to_coords(box1))
        polygon2 = Polygon(box_to_coords(box2))
        return polygon1.contains(polygon2)

    # Sort the boxes by area
    sorted_boxes = sorted(boxes, key=lambda box: (box[1] * box[0]), reverse=True)

    non_overlapping_boxes = []

    while sorted_boxes:
        first_item = sorted_boxes.pop(0)

        is_inside_other_polygon = False

        for box in sorted_boxes:
            if box_overlap(box, first_item):
                is_inside_other_polygon = True
                break

        if not is_inside_other_polygon:
            non_overlapping_boxes.append(first_item)

    return non_overlapping_boxes


def estimate_rows(boxes):
    non_overlapping_boxes = get_non_overlapping_boxes(boxes)

    # Sort the boxes based on y, then x
    sorted_boxes = sorted(non_overlapping_boxes, key=lambda box: (box[1], box[0]))

    rows = []

    while sorted_boxes:
        first_item = sorted_boxes.pop(0)

        col = [first_item]

        same_col_boxes = [box for box in sorted_boxes if first_item[1] <= box[1] <= (first_item[1] + first_item[3] / 2)]

        col.extend(same_col_boxes)

        for box in same_col_boxes:
            sorted_boxes.remove(box)

        col.sort(key=lambda box: box[0])

        rows.append(col)

    return rows


def mode(arr):
    most_freq = Counter(arr).most_common()
    return most_freq[0][0]


def estimate_reference_column(rows):
    if rows:
        row_lengths = [len(row) for row in rows]
        most_freq = mode(row_lengths)
        ele = [row for row in rows if len(row) == most_freq]
        return ele[0], most_freq

    return None


def cell_boundaries_along_x(max_len_col):
    return [(x + 0.5, x + w - 0.5) for x, _, w, _ in max_len_col]


def x_overlap_percentage(box, bound):
    x, y, w, h = box
    min_x, max_x = bound

    intersection = max(0, min(x + w, max_x) - max(x, min_x))
    overlap_percentage = (intersection / w) * 100

    return overlap_percentage


def estimate_cell_numbers(rows, cell_bounds):
    result_rows: list[list] = []
    min_bound_x = cell_bounds[0][0]
    max_bound_x = cell_bounds[-1][1]

    for row in rows:
        temp_col = []

        for box in row:
            x, _, _, _ = box

            if x < min_bound_x:
                cell_number = 0
            elif x >= max_bound_x:
                cell_number = len(cell_bounds) - 1
            else:
                _, cell_number = max(
                    ((x_overlap_percentage(box, bound), idx) for idx, bound in enumerate(cell_bounds)),
                    key=lambda x: x[0],
                )

            temp_col.append((cell_number, box))

        result_rows.append(temp_col)

    return result_rows


def get_rows_from_boxes(ocr_boxes: list[tuple[float, float, float, float]]):
    """
    Given a list of box (x, y, w, h), returns a tuple of the following:
    - number of rows,
    - number of cols,
    - list of estimated where each value is an index and box
    """

    table = get_table_bounding_box(ocr_boxes)

    new_boxes = filter_boxes(ocr_boxes, table)

    non_overlap_box = get_non_overlapping_boxes(new_boxes)

    if row_vals := estimate_rows(non_overlap_box):
        reference_col, num_cols = estimate_reference_column(row_vals)
        cell_boundaries = cell_boundaries_along_x(reference_col)
        rows_with_cell_numbers = estimate_cell_numbers(row_vals, cell_boundaries)
        num_rows = len(rows_with_cell_numbers)

        return num_rows, num_cols, rows_with_cell_numbers

    return None


def get_table_bounding_box(boxes):
    min_x = min(box[0] for box in boxes)
    min_y = min(box[1] for box in boxes)
    max_x = max(box[0] + box[2] for box in boxes)
    max_y = max(box[1] + box[3] for box in boxes)

    width = max_x - min_x
    height = max_y - min_y

    return min_x, min_y, width, height


def filter_boxes(boxes, table, min_row: int = 3, min_col: int = 2):
    table_width = table[2] / min_col
    table_height = table[3] / min_row
    table_area = (table[2] * table[3]) / (min_row * min_col)

    filtered_boxes = [
        box for box in boxes if box[2] < table_width and box[3] < table_height and (box[2] * box[3]) < table_area
    ]

    return filtered_boxes


if __name__ == "__main__":
    boxes = [
        [37, 0, 109, 2],
        [14, 10, 336, 342],
        [248, 15, 97, 23],
        [20, 15, 224, 24],
        [280, 18, 34, 16],
        [23, 19, 83, 16],
        [297, 24, 1, 4],
        [285, 24, 2, 1],
        [87, 25, 2, 4],
        [298, 41, 47, 26],
        [311, 41, 20, 14],
        [248, 41, 47, 26],
        [197, 41, 47, 27],
        [210, 41, 5, 14],
        [146, 41, 48, 27],
        [20, 42, 123, 27],
        [215, 42, 14, 11],
        [257, 47, 19, 14],
        [77, 48, 16, 15],
        [56, 48, 13, 15],
        [22, 48, 12, 15],
        [275, 48, 10, 13],
        [167, 48, 5, 13],
        [176, 49, 7, 11],
        [171, 49, 5, 11],
        [92, 50, 19, 13],
        [35, 51, 19, 15],
        [314, 51, 31, 16],
        [212, 52, 32, 16],
        [187, 55, 4, 1],
        [149, 55, 1, 2],
        [42, 55, 2, 3],
        [326, 58, 11, 3],
        [298, 70, 47, 23],
        [248, 71, 47, 22],
        [197, 71, 47, 22],
        [146, 71, 48, 22],
        [20, 71, 123, 23],
        [211, 75, 27, 15],
        [206, 75, 6, 15],
        [168, 75, 6, 15],
        [156, 75, 11, 15],
        [75, 75, 12, 15],
        [70, 75, 6, 16],
        [23, 75, 43, 18],
        [28, 80, 4, 1],
        [28, 85, 4, 1],
        [298, 121, 47, 23],
        [248, 121, 47, 23],
        [197, 122, 47, 22],
        [146, 122, 48, 22],
        [20, 122, 123, 23],
        [220, 125, 11, 15],
        [208, 125, 11, 15],
        [203, 125, 6, 15],
        [165, 125, 22, 18],
        [154, 125, 11, 15],
        [322, 125, 16, 15],
        [305, 125, 20, 15],
        [256, 125, 20, 15],
        [23, 126, 20, 15],
        [45, 127, 19, 14],
        [230, 128, 11, 15],
        [275, 128, 11, 15],
        [64, 129, 5, 12],
        [28, 131, 5, 1],
        [279, 132, 2, 3],
        [235, 133, 1, 2],
        [180, 133, 1, 2],
        [351, 138, 6, 14],
        [298, 147, 47, 22],
        [248, 147, 47, 23],
        [197, 147, 47, 23],
        [146, 147, 48, 23],
        [20, 148, 123, 23],
        [308, 150, 6, 16],
        [313, 151, 25, 15],
        [252, 151, 28, 15],
        [220, 151, 11, 15],
        [200, 151, 19, 15],
        [169, 151, 22, 18],
        [149, 151, 20, 15],
        [77, 152, 35, 15],
        [59, 152, 13, 15],
        [23, 152, 32, 15],
        [353, 153, 5, 20],
        [279, 153, 11, 16],
        [230, 154, 11, 15],
        [54, 155, 5, 12],
        [261, 156, 5, 5],
        [209, 156, 5, 5],
        [71, 158, 5, 12],
        [283, 158, 2, 1],
        [235, 159, 1, 2],
        [184, 159, 1, 2],
        [93, 162, 2, 1],
        [352, 175, 5, 11],
        [298, 250, 47, 22],
        [248, 250, 47, 22],
        [197, 250, 47, 22],
        [146, 250, 48, 23],
        [20, 251, 123, 23],
        [313, 254, 25, 15],
        [308, 254, 6, 15],
        [256, 254, 20, 15],
        [216, 254, 11, 15],
        [204, 254, 11, 15],
        [165, 254, 21, 18],
        [158, 254, 5, 11],
        [23, 255, 34, 15],
        [275, 257, 11, 15],
        [226, 257, 11, 15],
        [279, 261, 1, 3],
        [231, 262, 1, 2],
        [180, 262, 1, 2],
        [318, 263, 1, 1],
        [153, 264, 11, 5],
        [298, 275, 47, 22],
        [248, 275, 47, 22],
        [197, 276, 47, 21],
        [146, 276, 48, 21],
        [20, 276, 123, 22],
        [212, 279, 19, 15],
        [161, 279, 29, 18],
        [316, 279, 6, 15],
        [305, 279, 11, 15],
        [266, 279, 12, 15],
        [254, 279, 12, 15],
        [200, 280, 11, 14],
        [155, 280, 5, 13],
        [150, 280, 5, 14],
        [37, 280, 37, 15],
        [322, 280, 16, 14],
        [22, 281, 16, 14],
        [230, 282, 11, 15],
        [277, 282, 11, 15],
        [281, 286, 1, 1],
        [235, 287, 1, 2],
        [184, 287, 1, 2],
        [44, 287, 2, 3],
        [20, 325, 325, 22],
        [117, 329, 23, 14],
        [77, 329, 39, 15],
        [168, 330, 20, 13],
        [23, 330, 29, 14],
        [143, 331, 21, 12],
        [63, 331, 15, 12],
        [52, 334, 11, 8],
    ]

    row_count, col_count, rows = get_rows_from_boxes(boxes)

    print(row_count, col_count, rows, sep="\n")
