import pytest
from src.extractor import extract_and_format_date

@pytest.mark.parametrize("input_text,expected", [
    # Các trường hợp thực tế thường gặp trên hóa đơn
    ("Ngày 10 tháng 07 năm 2025", "10/07/2025"),
    ("Ngày 14 tháng 07 năm 2025", "14/07/2025"),
    ("Ngày 12 tháng 07 năm 2025", "12/07/2025"),
    ("Ngày 07 tháng 07 năm 2025", "07/07/2025"),
    ("Ngày 15 tháng 7 năm 2025", "15/07/2025"),
    ("Ngày 5 tháng 07 năm 2025", "05/07/2025"),
    ("Ngày 5 tháng 7 năm 2025", "05/07/2025"),
    ("ngày 7 tháng 7 năm 2023", "07/07/2023"),
    ("ngày 31 tháng 12 năm 2022", "31/12/2022"),
    ("Ngày: 01 tháng 1 năm 2020", "01/01/2020"),
    ("Ngày: 1 tháng 1 năm 2020", "01/01/2020"),
    # Định dạng số ngắn
    ("01/01/2020", "01/01/2020"),
    ("07-07-2023", "07/07/2023"),
    ("2023/07/07", None),  # Không đúng định dạng dd/mm/yyyy
    ("07.07.2023", "07/07/2023"),
    (" 07/07/2023 ", "07/07/2023"),
    # Trường hợp không hợp lệ
    ("Ngày (day) 10 tháng (month) 07 năm (year) 2025", "10/07/2025"),
    ("Ngày (date) 14 tháng (month) 07 năm (year) 2025", "14/07/2025"),
    ("Ngày (Date) 12 tháng (month) 07 năm (year) 2025", "12/07/2025"),
    ("Ngày (Date) 5 tháng (month) 07 năm (year) 2025", "05/07/2025"),
    ("7/7", None),                # Thiếu năm
    ("2023", None),              # Chỉ có năm
    ("32/13/2023", None),        # Ngày/tháng không hợp lệ
    ("abc", None),               # Không phải ngày
    ("", None),                  # Chuỗi rỗng
    (None, None),                 # None
])
def test_extract_and_format_date(input_text, expected):
    assert extract_and_format_date(input_text) == expected 