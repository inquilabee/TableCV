from dataclasses import dataclass

from shapely.geometry import Polygon

type BoundingBoxTuple = tuple[float, float, float, float]
type OCRResult = tuple[BoundingBoxTuple, str]


@dataclass(frozen=True, slots=True)
class BoundingBox:
    x: float
    y: float
    width: float
    height: float

    @classmethod
    def from_tuple(cls, bounds: "BoundingBox | BoundingBoxTuple") -> "BoundingBox":
        if isinstance(bounds, BoundingBox):
            return bounds

        x, y, width, height = bounds
        return cls(x=float(x), y=float(y), width=float(width), height=float(height))

    @property
    def as_tuple(self) -> BoundingBoxTuple:
        return self.x, self.y, self.width, self.height

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def max_x(self) -> float:
        return self.x + self.width

    @property
    def max_y(self) -> float:
        return self.y + self.height

    @property
    def coords(self) -> list[tuple[float, float]]:
        return [(self.x, self.y), (self.max_x, self.y), (self.max_x, self.max_y), (self.x, self.max_y)]

    @property
    def polygon(self) -> Polygon:
        return Polygon(self.coords)

    def contains(self, other: "BoundingBox | BoundingBoxTuple") -> bool:
        return self.polygon.contains(BoundingBox.from_tuple(other).polygon)

    def x_overlap_percentage(self, bounds: tuple[float, float]) -> float:
        if self.width <= 0:
            return 0

        min_x, max_x = bounds
        intersection = max(0, min(self.max_x, max_x) - max(self.x, min_x))
        return (intersection / self.width) * 100


@dataclass(frozen=True, slots=True)
class TextBox:
    box: BoundingBox
    text: str

    @classmethod
    def from_ocr_result(cls, result: OCRResult) -> "TextBox":
        bounds, text = result
        return cls(box=BoundingBox.from_tuple(bounds), text=text)

    @property
    def bounds(self) -> BoundingBoxTuple:
        return self.box.as_tuple

    @property
    def x(self) -> float:
        return self.box.x

    @property
    def y(self) -> float:
        return self.box.y

    @property
    def width(self) -> float:
        return self.box.width

    @property
    def height(self) -> float:
        return self.box.height
