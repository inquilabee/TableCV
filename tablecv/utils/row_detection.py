from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from tablecv.types import BoundingBox, BoundingBoxTuple

type BoundingBoxLike = BoundingBox | BoundingBoxTuple


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


def non_overlapping_boxes(boxes: Sequence[BoundingBoxLike]) -> list[BoundingBox]:
    sorted_boxes = sorted((BoundingBox.from_tuple(box) for box in boxes), key=lambda box: box.area, reverse=True)
    result = []

    while sorted_boxes:
        candidate = sorted_boxes.pop(0)
        is_inside_other_box = any(box.contains(candidate) for box in sorted_boxes)

        if not is_inside_other_box:
            result.append(candidate)

    return result


def estimate_rows(boxes: Sequence[BoundingBoxLike]) -> list[RowCluster]:
    sorted_boxes = sorted(non_overlapping_boxes(boxes), key=lambda box: (box.y, box.x))
    rows = []

    while sorted_boxes:
        first_box = sorted_boxes.pop(0)
        same_row_boxes = boxes_in_same_row(first_box, sorted_boxes)
        rows.append(RowCluster.from_boxes([first_box, *same_row_boxes]))
        remove_boxes(sorted_boxes, same_row_boxes)

    return rows


def boxes_in_same_row(first_box: BoundingBox, boxes: list[BoundingBox]) -> list[BoundingBox]:
    return [box for box in boxes if first_box.y <= box.y <= first_box.y + first_box.height / 2]


def remove_boxes(boxes: list[BoundingBox], boxes_to_remove: list[BoundingBox]) -> None:
    for box in boxes_to_remove:
        boxes.remove(box)


def estimate_reference_row(rows: list[RowCluster]) -> tuple[RowCluster, int]:
    if not rows:
        return RowCluster([]), 0

    most_common_length = mode([row.length for row in rows])
    reference_rows = [row for row in rows if row.length == most_common_length]
    return reference_rows[0], most_common_length


def mode(values: list[int]) -> int:
    return Counter(values).most_common(1)[0][0]
