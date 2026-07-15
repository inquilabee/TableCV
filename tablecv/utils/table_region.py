from collections import Counter
from statistics import median

from tablecv.utils.row_detection import RowCluster, estimate_reference_row


def select_table_rows(rows: list[RowCluster], min_row: int, min_col: int) -> list[RowCluster]:
    candidate_runs = table_row_runs(rows, min_row, min_col)
    if not candidate_runs:
        return rows

    return max(candidate_runs, key=score_row_run)


def table_row_runs(rows: list[RowCluster], min_row: int, min_col: int) -> list[list[RowCluster]]:
    multi_cell_rows = [row for row in rows if row.length >= min_col]
    if not multi_cell_rows:
        return []

    return contiguous_table_runs(multi_cell_rows, max_table_row_gap(multi_cell_rows), min_row)


def contiguous_table_runs(rows: list[RowCluster], max_row_gap: float, min_row: int) -> list[list[RowCluster]]:
    runs = []
    current_run: list[RowCluster] = []

    for row in rows:
        if not current_run or row_belongs_to_run(row, current_run, max_row_gap):
            current_run.append(row)
        else:
            append_table_run(runs, current_run, min_row)
            current_run = [row]

    append_table_run(runs, current_run, min_row)
    return runs


def append_table_run(runs: list[list[RowCluster]], current_run: list[RowCluster], min_row: int) -> None:
    if len(current_run) >= min_row:
        runs.append(current_run)


def row_belongs_to_run(row: RowCluster, current_run: list[RowCluster], max_row_gap: float) -> bool:
    return row_y(row) - row_y(current_run[-1]) <= max_row_gap


def max_table_row_gap(rows: list[RowCluster]) -> float:
    positive_gaps = positive_row_gaps(rows)
    return row_gap_limit(positive_gaps, typical_row_height(rows))


def positive_row_gaps(rows: list[RowCluster]) -> list[float]:
    y_values = [row_y(row) for row in rows]
    return [current - previous for previous, current in zip(y_values, y_values[1:], strict=False) if current > previous]


def typical_row_height(rows: list[RowCluster]) -> float:
    return median(row_height(row) for row in rows)


def row_gap_limit(positive_gaps: list[float], typical_height: float) -> float:
    if not positive_gaps:
        return typical_height * 3

    return max(median(positive_gaps) * 2.5, typical_height * 3)


def row_y(row: RowCluster) -> float:
    return min(box.y for box in row.boxes)


def row_height(row: RowCluster) -> float:
    return max(box.height for box in row.boxes)


def score_row_run(rows: list[RowCluster]) -> float:
    row_lengths = [row.length for row in rows]
    length_counts = Counter(row_lengths)
    repeated_length, repeated_count = max(length_counts.items(), key=lambda item: (item[0] * item[1], item[0]))
    total_cells = sum(row_lengths)
    return repeated_length * repeated_count + total_cells / 100


def trim_rows_before_reference(rows: list[RowCluster], reference_row: RowCluster) -> list[RowCluster]:
    if not reference_row.boxes:
        return rows

    try:
        reference_index = rows.index(reference_row)
    except ValueError:
        return rows

    return rows[reference_index:]


def estimate_table_reference_row(rows: list[RowCluster], min_row: int, min_col: int) -> tuple[RowCluster, int]:
    if not rows:
        return RowCluster([]), 0

    row_lengths = Counter(row.length for row in rows)
    longest_row_length = max(row_lengths)
    return reference_from_table_patterns(rows, row_lengths, longest_row_length, min_row, min_col)


def reference_from_table_patterns(
    rows: list[RowCluster],
    row_lengths: Counter[int],
    longest_row_length: int,
    min_row: int,
    min_col: int,
) -> tuple[RowCluster, int]:
    if rows[0].length == longest_row_length:
        return rows[0], longest_row_length

    if row_lengths[longest_row_length] >= 2:
        return reference_row_with_length(rows, longest_row_length)

    if repeated_lengths := repeated_row_lengths(row_lengths, min_row, min_col):
        return reference_row_with_length(rows, best_repeated_length(repeated_lengths))

    return estimate_reference_row(rows)


def repeated_row_lengths(row_lengths: Counter[int], min_row: int, min_col: int) -> dict[int, int]:
    return {
        length: count
        for length, count in row_lengths.items()
        if is_repeated_table_length(length, count, min_row, min_col)
    }


def is_repeated_table_length(length: int, count: int, min_row: int, min_col: int) -> bool:
    return length >= min_col and count >= min_row


def best_repeated_length(repeated_lengths: dict[int, int]) -> int:
    column_count, _ = max(repeated_lengths.items(), key=lambda item: (item[0] * item[1], item[0]))
    return column_count


def reference_row_with_length(rows: list[RowCluster], length: int) -> tuple[RowCluster, int]:
    reference_rows = [row for row in rows if row.length == length]
    return reference_rows[0], length
