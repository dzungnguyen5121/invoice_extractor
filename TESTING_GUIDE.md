# 🧪 HƯỚNG DẪN KIỂM THỬ TỰ ĐỘNG

## 1. Cài đặt môi trường kiểm thử

- Đảm bảo đã cài Python ≥ 3.7
- Cài đặt pytest:
  ```bash
  pip install pytest
  ```

## 2. Thiết lập biến môi trường PYTHONPATH

Để các file test nhận diện đúng module `src`, bạn cần thiết lập biến môi trường `PYTHONPATH` về thư mục gốc dự án.

**Trên Windows (PowerShell):**
```powershell
$env:PYTHONPATH="D:\rat_la_tu_dong\rat_la_tu_dong"
```
**Trên Windows (cmd):**
```cmd
set PYTHONPATH=D:\rat_la_tu_dong\rat_la_tu_dong
```
**Trên Linux/macOS:**
```bash
export PYTHONPATH=.
```

## 3. Chạy toàn bộ kiểm thử

Chạy tất cả các test (unit + integration):

```bash
pytest
```

## 4. Chạy kiểm thử đơn vị (unit test)

Chạy toàn bộ test trong thư mục `tests/unit`:
```bash
pytest tests/unit
```

Chạy một file test cụ thể, ví dụ:
```bash
pytest tests/unit/test_extractor_format_date.py
```

## 5. Chạy kiểm thử tích hợp (integration test)

Chạy toàn bộ test trong thư mục `tests/integration`:
```bash
pytest tests/integration
```

Chạy một file test cụ thể:
```bash
pytest tests/integration/extractor/test_extract_pdf.py
```

## 6. Ý nghĩa các file kiểm thử đơn vị

- **test_extractor_format_date.py**: Kiểm tra hàm chuẩn hóa/trích xuất ngày tháng từ chuỗi văn bản.
- **test_extractor_parse_number.py**: Kiểm tra hàm chuyển đổi chuỗi số (có thể có dấu phân cách kiểu Việt Nam/quốc tế) thành số thực.
- **test_extractor_normalize_fuzzy.py**: Kiểm tra hàm chuẩn hóa/mapping tên cột bảng bằng so khớp mờ.
- **test_extractor_normalize_header.py**: Kiểm tra hàm chuẩn hóa tiêu đề bảng.

## 7. Đọc kết quả kiểm thử

- Nếu tất cả test đều **PASSED**: Hệ thống hoạt động đúng với các trường hợp kiểm thử.
- Nếu có test **FAILED**: Pytest sẽ hiển thị chi tiết lỗi, ví dụ:
  ```
  AssertionError: Field date: expected 07/07/2023, got 07/07/2025
  ```
  → So sánh lại dữ liệu mong đợi và kết quả thực tế, kiểm tra lại logic code hoặc dữ liệu test.

## 8. Thêm kiểm thử mới

- Tạo file mới trong `tests/unit/` hoặc `tests/integration/` với tên bắt đầu bằng `test_`.
- Viết hàm test bắt đầu bằng `test_`.
- Sử dụng `pytest.mark.parametrize` để kiểm thử nhiều trường hợp đầu vào/đầu ra.

**Ví dụ kiểm thử đơn giản:**
```python
import pytest
from src.extractor import parse_number

@pytest.mark.parametrize("input_str,expected", [
    ("1.000,50", 1000.5),
    ("2,5", 2.5),
    ("abc", 0.0),
])
def test_parse_number(input_str, expected):
    assert parse_number(input_str) == expected
```

## 9. Một số lưu ý

- Nếu gặp lỗi import, hãy kiểm tra lại biến môi trường `PYTHONPATH`.
- Đảm bảo các file test và module đều có tên hợp lệ (không có ký tự lạ, không thiếu `__init__.py` nếu cần).
- Có thể thêm option `-v` để xem chi tiết từng test:
  ```bash
  pytest -v
  ```

---

**Mọi thắc mắc về kiểm thử, hãy kiểm tra lại log lỗi hoặc liên hệ người phát triển dự án.** 