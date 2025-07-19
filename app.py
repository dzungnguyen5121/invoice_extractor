import pdfplumber
import openpyxl
import os
import re
import json
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import unicodedata
from src.excel import save_to_excel
from src.extractor import extract_data_from_pdf
from src.config import load_config, setup_logger
import uuid

# Thay thế phần cấu hình logger:
logger = setup_logger('logs/invoices.log')
# log_handler = RotatingFileHandler('invoices.log', maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
# log_handler.setLevel(logging.INFO)  # Mặc định chỉ log INFO trở lên
# log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# log_handler.setFormatter(log_formatter)
# if not logger.hasHandlers():
#     logger.addHandler(log_handler)
# logger.setLevel(logging.INFO)
# Giảm mức log của pdfminer và pdfplumber để tránh log rác
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)

app = Flask(__name__)
app.secret_key = 'local_dev_key'  # Đơn giản, chỉ dùng cho local
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
CONFIG_FILE = 'config.json'
config = load_config(CONFIG_FILE)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Đọc file cấu hình JSON
# try:
#     with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
#         config = json.load(f)
# except Exception as e:
#     logger.error(f"Failed to load config.json: {e}")
#     config = {'default': {}}

# Biến toàn cục lưu dữ liệu hóa đơn tạm thời và tên file PDF gốc
current_invoice_data = []
current_invoice_filename = ""

# Giao diện web
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global current_invoice_data, current_invoice_filename
    files = request.files.getlist('files')
    data_list = []
    errors = []
    for file in files:
        if file and file.filename.endswith('.pdf'):
            filename = file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            data, file_errors = extract_data_from_pdf(file_path, config)
            data_list.extend(data)
            errors.extend(file_errors)
            current_invoice_filename = os.path.splitext(filename)[0]  # Lưu tên không đuôi .pdf
        else:
            errors.append(f"Invalid file: {file.filename}")
    # Lưu dữ liệu vào biến toàn cục
    current_invoice_data = data_list
    return render_template('result.html', data=data_list, errors=errors)

@app.route('/download')
def download():
    global current_invoice_data, current_invoice_filename
    if not current_invoice_data:
        return "No invoice data found", 400
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"{current_invoice_filename}_{timestamp}.xlsx"
    excel_path = os.path.join(OUTPUT_FOLDER, excel_filename)
    save_to_excel(current_invoice_data, excel_path)
    return send_file(excel_path, as_attachment=True, download_name=excel_filename)

# Thêm route để reset dữ liệu tạm và trở về trang chính
@app.route('/reset')
def reset():
    global current_invoice_data
    current_invoice_data = []
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)