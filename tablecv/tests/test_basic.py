from tablecv import extract_table


def test_basic():
    img_path = r"/Users/dayhatt/workspace/projects/food_ocr/food_ocr/media/column_table2.png"
    print(extract_table(img_path))
