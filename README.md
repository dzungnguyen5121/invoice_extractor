# Hệ thống Tự động Đọc Hóa đơn PDF

Hệ thống tự động hóa việc đọc và trích xuất dữ liệu từ hóa đơn PDF, sau đó xuất ra file Excel để quản lý và phân tích.

## 🚀 Tính năng chính

- **Tự động trích xuất dữ liệu** từ hóa đơn PDF
- **Xử lý nhiều file cùng lúc** 
- **Lưu trữ dữ liệu** vào cơ sở dữ liệu SQLite
- **Xuất ra file Excel** với định dạng chuẩn
- **Giao diện web** dễ sử dụng
- **Cấu hình linh hoạt** thông qua file JSON
- **Xử lý lỗi** và logging chi tiết

## 📋 Yêu cầu hệ thống

- Python 3.7 trở lên
- Windows/Linux/macOS

## 🛠️ Cài đặt

### 1. Clone hoặc tải dự án
```bash
git clone <repository-url>
cd rat_la_tu_dong
```

### 2. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 3. Cấu trúc thư mục
Đảm bảo có các thư mục sau:
```
rat_la_tu_dong/
├── app.py
├── src/
│   ├── config.py
│   ├── db.py
│   ├── excel.py
│   └── extractor.py
├── config.json
├── invoices.db
├── logs/
│   ├── invoices.log
│   └── invoices.log.5
├── templates/
│   ├── index.html
│   └── result.html
├── uploads/          # Tự động tạo
├── output/           # Tự động tạo
└── README.md
```

## 🚀 Chạy ứng dụng

### 1. Khởi động server
```bash
python app.py
```

### 2. Truy cập ứng dụng
Mở trình duyệt và truy cập: `http://localhost:5000`

## 📖 Hướng dẫn sử dụng

### 1. Upload hóa đơn PDF
- Truy cập trang chủ
- Chọn file PDF cần xử lý (có thể chọn nhiều file)
- Nhấn nút "Process" để bắt đầu xử lý

### 2. Xem kết quả
- Sau khi xử lý, hệ thống hiển thị:
  - Bảng dữ liệu đã trích xuất
  - Danh sách lỗi (nếu có)
  - Nút download file Excel

### 3. Download file Excel
- Nhấn nút "Download Excel" để tải file `invoices.xlsx`
- File được lưu trong thư mục `output/`

## ⚙️ Cấu hình

### File config.json
Chỉnh sửa file `config.json` để phù hợp với định dạng hóa đơn:

```json
{
  "default": {
    "tax_code": "Mã số thuế: (\\d{10}[\\w\\.]*)",
    "invoice_number": "Số hóa đơn: (\\d+)",
    "date": "Ngày: (\\d{2}/\\d{2}/\\d{4})",
    "company_name": "Công ty: (.+?)\\n",
    "tax_rate": "Thuế: (\\d+) ?%",
    "table_columns": {
      "item_name": ["Tên hàng hóa", "Description"],
      "unit": ["Đơn vị tính", "Unit"],
      "quantity": ["Số lượng", "Quantity"],
      "unit_price": ["Đơn giá", "Unit Price"],
      "subtotal": ["Thành tiền", "Amount"]
    }
  }
}
```

### Các trường cấu hình:
- **tax_code**: Regex để tìm mã số thuế
- **invoice_number**: Regex để tìm số hóa đơn
- **date**: Regex để tìm ngày tháng
- **company_name**: Regex để tìm tên công ty
- **tax_rate**: Regex để tìm thuế suất
- **table_columns**: Mapping tên cột trong bảng

## 📊 Cấu trúc dữ liệu

### Database Schema (SQLite)
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,                    -- Ngày hóa đơn
    tax_code TEXT,                -- Mã số thuế
    invoice_number TEXT,          -- Số hóa đơn
    company_name TEXT,            -- Tên công ty
    item_name TEXT,               -- Tên hàng hóa
    unit TEXT,                    -- Đơn vị tính
    quantity REAL,                -- Số lượng
    unit_price REAL,              -- Đơn giá
    subtotal REAL,                -- Thành tiền
    tax_rate REAL,                -- Thuế suất
    tax_amount REAL,              -- Tiền thuế
    total REAL,                   -- Tổng tiền
    category TEXT                 -- Phân loại
);
```

### Excel Output
File Excel chứa các cột:
1. STT
2. Ngày tháng năm
3. Mã số thuế
4. Số hóa đơn
5. Tên công ty
6. Tên hàng
7. Đơn vị
8. Số lượng
9. Đơn giá
10. Thành tiền
11. % Thuế
12. Tiền thuế
13. Tổng tiền
14. Phân loại

## 🔧 Tùy chỉnh nâng cao

### 1. Thêm định dạng hóa đơn mới
Chỉnh sửa `config.json` để thêm patterns mới:

```json
{
  "default": {
    "tax_code": "Mã số thuế: (\\d{10}[\\w\\.]*)|Tax Code: (\\d{10}[\\w\\.]*)",
    "invoice_number": "Số hóa đơn: (\\d+)|Invoice No: (\\d+)"
  }
}
```

### 2. Xử lý định dạng số đặc biệt
Chỉnh sửa hàm `parse_number()` trong `src/extractor.py`:

```python
def parse_number(value):
    # Thêm logic xử lý định dạng số đặc biệt
    value = value.replace('.', '').replace(',', '.')
    return float(value)
```

### 3. Thêm validation dữ liệu
Thêm kiểm tra trong hàm `extract_data_from_pdf()`:

```python
# Kiểm tra dữ liệu bắt buộc
if not data['tax_code'] or not data['invoice_number']:
    errors.append("Missing required fields")
```

## 🐛 Xử lý lỗi thường gặp

### 1. Lỗi "No tables found"
- **Nguyên nhân**: PDF không có bảng hoặc định dạng không nhận diện được
- **Giải pháp**: Kiểm tra định dạng PDF, có thể cần OCR

### 2. Lỗi "Missing required fields"
- **Nguyên nhân**: Regex patterns không khớp với hóa đơn
- **Giải pháp**: Cập nhật patterns trong `config.json`

### 3. Lỗi "Invalid file"
- **Nguyên nhân**: File không phải PDF
- **Giải pháp**: Chỉ upload file PDF

## 📝 Logging

Hệ thống tự động log các hoạt động vào file `logs/invoices.log`:
- Thông tin xử lý file
- Lỗi và cảnh báo
- Số lượng record đã xử lý

## 🔒 Bảo mật

- File upload được validate và sanitize
- Chỉ chấp nhận file PDF
- Sử dụng `secure_filename()` để tránh path traversal

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra file log `logs/invoices.log`
2. Đảm bảo cấu hình `config.json` phù hợp
3. Kiểm tra định dạng hóa đơn PDF

## 📄 License

Dự án này được phát triển cho mục đích học tập và sử dụng nội bộ.

---

**Lưu ý**: Đảm bảo tuân thủ các quy định về bảo mật dữ liệu khi xử lý hóa đơn chứa thông tin nhạy cảm. 

## 🧪 Kiểm thử tự động với pytest

Để chạy các kiểm thử tự động, hãy đảm bảo bạn đã cài pytest:
```bash
pip install pytest
```

**Chạy test (Windows):**
```bash
set PYTHONPATH=.
pytest
```

**Chạy test (Linux/macOS):**
```bash
PYTHONPATH=. pytest
```

Nếu bạn không thiết lập PYTHONPATH, các import kiểu `from src.xxx import ...` trong file test sẽ bị lỗi. 