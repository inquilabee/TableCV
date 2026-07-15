from collections.abc import Mapping
from numbers import Number
from pathlib import Path
from typing import Any

import pandas as pd

from tablecv.types import OCRResult
from tablecv.utils.table_extraction import extract_table_from_ocr


def _create_paddle_ocr():
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        msg = (
            'PaddleOCR is required for extract_table(). Install it with: pip install "tablecv[paddle]". '
            "On Linux, PaddlePaddle may also require the system OpenMP runtime, such as libgomp1."
        )
        raise ImportError(msg) from exc

    try:
        return PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=True,
            enable_mkldnn=False,
        )
    except TypeError:
        return PaddleOCR(use_angle_cls=True)


def _standardize_box(coords: Any) -> tuple[float, float, float, float]:
    if _is_corner_box(coords):
        return _standardize_corner_box(coords)

    return _standardize_polygon_box(coords)


def _is_corner_box(coords: Any) -> bool:
    return len(coords) == 4 and all(isinstance(value, Number) for value in coords)


def _standardize_corner_box(coords: Any) -> tuple[float, float, float, float]:
    x_min, y_min, x_max, y_max = (float(value) for value in coords)
    return x_min, y_min, x_max - x_min, y_max - y_min


def _standardize_polygon_box(coords: Any) -> tuple[float, float, float, float]:
    points = list(coords)
    x_values = [float(point[0]) for point in points]
    y_values = [float(point[1]) for point in points]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    return x_min, y_min, x_max - x_min, y_max - y_min


def _mapping_from_result(result: Any) -> Mapping[str, Any] | None:
    if isinstance(result, Mapping):
        return result

    for attr_name in ("res", "json"):
        value = getattr(result, attr_name, None)
        if callable(value):
            value = value()
        if isinstance(value, Mapping):
            return value

    return None


def _first_present(result: Mapping[str, Any], keys: tuple[str, ...]) -> Any | None:
    for key in keys:
        value = result.get(key)
        if value is not None:
            return value
    return None


def _items_from_mapping(result: Mapping[str, Any]) -> list[OCRResult]:
    boxes = _first_present(result, ("dt_polys", "rec_polys", "rec_boxes", "boxes"))
    texts = _first_present(result, ("rec_texts", "texts"))
    if boxes is None or texts is None:
        return []

    return [(_standardize_box(box), str(text)) for box, text in zip(boxes, texts, strict=False)]


def _items_from_legacy_page(page: Any) -> list[OCRResult]:
    items = []
    for item in page:
        box, text_result = item
        text = text_result[0] if isinstance(text_result, list | tuple) else text_result
        items.append((_standardize_box(box), str(text)))
    return items


def _extract_ocr_items(result: Any) -> list[OCRResult]:
    items = []
    for page in result or []:
        if mapping := _mapping_from_result(page):
            items.extend(_items_from_mapping(mapping))
        else:
            items.extend(_items_from_legacy_page(page))
    return items


def text_box_from_ocr(image_path: str | Path, ocr_engine: Any | None = None) -> list[OCRResult]:
    """Return OCR text as ``((x, y, width, height), text)`` tuples."""
    engine = ocr_engine or _create_paddle_ocr()
    if hasattr(engine, "predict"):
        result = engine.predict(input=str(image_path))
    else:
        result = engine.ocr(str(image_path), cls=True)
    return _extract_ocr_items(result)


def extract_table(image_path: str | Path, ocr_engine: Any | None = None) -> pd.DataFrame:
    ocr = text_box_from_ocr(image_path, ocr_engine=ocr_engine)
    return extract_table_from_ocr(ocr)
