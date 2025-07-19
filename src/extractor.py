import pdfplumber
import re
import unicodedata
import json
import logging

# Hàm xử lý chuỗi số
def parse_number(value):
    try:
        if not value or '=' in value:
            return 0.0
        value = str(value).strip().replace(' ', '')
        # Kiểu quốc tế: nhiều dấu phẩy ngăn cách ngàn, 1 dấu chấm thập phân ở cuối
        if value.count(',') >= 1 and value.count('.') == 1 and value.rfind('.') > value.rfind(','):
            int_part, dec_part = value.rsplit('.', 1)
            if all(len(x) == 3 for x in int_part.split(',')[1:]) or len(int_part.split(',')) == 1:
                value = int_part.replace(',', '') + '.' + dec_part
            else:
                return 0.0
        # Kiểu Việt Nam: nhiều dấu chấm ngăn cách ngàn, 1 dấu phẩy thập phân
        elif '.' in value and ',' in value:
            if value.count(',') == 1 and value.rfind(',') > value.rfind('.'):
                int_part, dec_part = value.rsplit(',', 1)
                if all(len(x) == 3 for x in int_part.split('.')[1:]) or len(int_part.split('.')) == 1:
                    value = int_part.replace('.', '') + '.' + dec_part
                else:
                    return 0.0
            else:
                return 0.0
        elif ',' in value:
            if value.count(',') == 1:
                # Một dấu phẩy, giả định là thập phân
                value = value.replace(',', '.')
            elif all(len(x) == 3 for x in value.split(',')[1:]) or len(value.split(',')) == 1:
                # Nhiều dấu phẩy, ngăn cách ngàn
                value = value.replace(',', '')
            else:
                return 0.0
        elif '.' in value:
            if value.count('.') == 1:
                # Một dấu chấm, giả định là thập phân
                pass
            elif all(len(x) == 3 for x in value.split('.')[1:]) or len(value.split('.')) == 1:
                # Nhiều dấu chấm, ngăn cách ngàn
                value = value.replace('.', '')
            else:
                return 0.0
        # Nếu còn ký tự lạ
        if not re.match(r'^-?\d*\.?\d*$', value):
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def extract_and_format_date(text):
    """
    Trích xuất và chuẩn hóa ngày tháng từ text về dạng dd/mm/yyyy.
    Trả về None nếu không nhận diện được hoặc ngày/tháng không hợp lệ.
    """
    if not text or not isinstance(text, str):
        return None
    patterns = [
        r"Ngày[^0-9]{0,20}(\d{1,2})[^0-9]{0,20}(\d{1,2})[^0-9]{0,20}(\d{4})",
        r"([0-9]{1,2})[\/\-. ]([0-9]{1,2})[\/\-. ]([0-9]{4})",
        r"Ngày[ :]*(\d{1,2}) tháng (\d{1,2}) năm (\d{4})",
        r"ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})"
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                day, month, year = match.groups()
                day, month = int(day), int(month)
                # Kiểm tra hợp lệ ngày/tháng
                if not (1 <= day <= 31 and 1 <= month <= 12):
                    return None
                return f"{day:02d}/{month:02d}/{year}"
            except Exception as e:
                logging.error(f"Lỗi chuẩn hóa ngày: {e}")
                continue
    return None

# Hàm chuẩn hóa header bảng
def normalize_header(header):
    if not header:
        return ''
    h = header.replace('\n', ' ').replace('(', '').replace(')', '').replace(':', '').replace('.', '').strip().lower()
    h = re.sub(r'\s+', ' ', h)
    return h

# Hàm chuẩn hóa không dấu, viết thường, loại bỏ ký tự đặc biệt
def normalize_fuzzy(text):
    if not text:
        return ''
    text = text.replace('Đ', 'D').replace('đ', 'd')
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = text.replace('\n', ' ').replace(':', '').replace('.', '').replace('(', '').replace(')', '').replace('%', ' % ').lower()
    text = re.sub(r'[^a-z0-9% ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Đọc file cấu hình JSON
def load_config(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {config_file}: {e}")
        return {'default': {}}

# Hàm kiểm tra tên công ty hợp lệ
def is_valid_company_name(line):
    line = line.strip()
    if not line or len(line) < 10:
        return False
    if not re.search(r'[A-Z]', line):
        return False
    if re.search(r'\d{10,}', line):
        return False
    
    # Loại trừ các từ khóa không phải tên công ty
    exclude_keywords = [
        'VAT', 'INVOICE', 'HÓA ĐƠN', 'TAX', 'SỐ', 'MST', 'CODE', 'ADDRESS', 'ĐỊA CHỈ',
        'ACCOUNT', 'TÀI KHOẢN', 'PHONE', 'ĐIỆN THOẠI', 'PHÒNG',
        'PHIẾU', 'BILL', 'RECEIPT', 'BẢNG KÊ', 'BẢNG', 'PHỤ LỤC', 'KÝ HIỆU', 'MẪU SỐ',
        'SỐ HĐ', 'SỐ HÓA ĐƠN', 'SỐ:', 'NO:', '(VAT INVOICE)', '(INVOICE)', '(HÓA ĐƠN)',
        '(TAX INVOICE)', '(GTGT)', '(VAT)', '(TAX)', '(INVOICE)', '(RECEIPT)'
    ]
    
    # Kiểm tra từ khóa loại trừ (trừ 'CHI NHÁNH' và 'CỬA HÀNG' vì có thể là phần của tên công ty)
    if any(kw in line.upper() for kw in exclude_keywords):
        return False
    
    # Kiểm tra đặc biệt cho 'CHI NHÁNH' và 'CỬA HÀNG' - chỉ loại trừ khi đứng một mình
    line_upper = line.upper()
    if line_upper.strip() in ['CHI NHÁNH', 'CỬA HÀNG']:
        return False
    
    # Loại trừ dòng chứa pattern ngày tháng
    date_patterns = [
        r'Ngày.*tháng.*năm',
        r'ngày.*tháng.*năm',
        r'Ngày.*month.*year',
        r'ngày.*month.*year'
    ]
    for pattern in date_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return False
    
    if re.match(r'^[\(\):\-]+', line) or re.match(r'[\(\):\-]+$', line):
        return False
    if len(line.split()) < 3:
        return False
    if not re.search(r'[A-Za-zÀ-ỹ]', line):
        return False
    return True

# Hàm trích xuất dữ liệu từ PDF
def extract_data_from_pdf(pdf_path, config):
    data_list = []
    default_config = config.get('default', {})
    errors = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            lines = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text
                lines += page_text.split('\n')
            # Trích xuất ngày
            date = extract_and_format_date(text) or ''
            # Trích xuất số hóa đơn
            def is_excluded_invoice_line(line, exclude_keywords):
                l = line.lower()
                return any(kw in l for kw in exclude_keywords)

            invoice_number = re.search(default_config.get('invoice_number', ''), text)
            invoice_number_val = invoice_number.group(1) if invoice_number else ''
            if not invoice_number_val:
                # Ưu tiên các dòng bắt đầu bằng 'Số:' hoặc có dạng 'Số: <số>', loại bỏ dòng chứa '/'
                for line in lines:
                    l = line.strip().lower()
                    if (l.startswith('số:') or 'số:' in l) and '/' not in l:
                        m = re.search(r'số:\s*(\d{1,10})', line, re.IGNORECASE)
                        if m:
                            invoice_number_val = m.group(1)
                            break
            # Gom danh sách loại trừ chung
            exclude_keywords = [
                'tài khoản', 'điện thoại', 'cửa hàng', 'xe', 'thuế', 'lượng', 'mã số thuế', 'tax code', 'mst',
                'account number', 'phone', 'quantity', 'address', 'địa chỉ', 'license plate',
                'số tài khoản', 'số điện thoại', 'số lượng', 'số nhà', 'số xe', 'biển số',
                'số phiếu', 'số hợp đồng', 'số chứng từ', 'số bảng kê', 'số phụ lục', 'số mẫu', 'số ký hiệu'
            ]
            if not invoice_number_val:
                invoice_keywords = ['số hóa đơn', 'số hoá đơn', 'số hđ', 'invoice no', 'invoice number', 'số:']
                for line in lines:
                    l = line.lower()
                    if any(kw in l for kw in invoice_keywords) and not is_excluded_invoice_line(line, exclude_keywords):
                        m = re.search(r'(\d{1,10})', line)
                        if m:
                            invoice_number_val = m.group(1)
                            break
            if not invoice_number_val:
                for line in lines:
                    l = line.lower()
                    if 'số' in l and not is_excluded_invoice_line(line, exclude_keywords):
                        m = re.search(r'(\d{1,10})', line)
                        if m:
                            invoice_number_val = m.group(1)
                            break
            # Trích xuất mã số thuế
            tax_code_match = re.search(default_config.get('tax_code', ''), text)
            tax_code = ''
            if tax_code_match:
                for g in tax_code_match.groups():
                    if g:
                        # Chỉ loại bỏ khoảng trắng và giữ nguyên số 0 ở đầu
                        tax_code = g.replace(' ', '').strip()
                        break
            # Trích xuất tên công ty
            company_name = ''
            tax_line_idx = next((i for i, l in enumerate(lines) if 'Mã số thuế' in l or 'Tax Code' in l or 'MST' in l), None)
            if tax_line_idx and tax_line_idx > 0:
                prev_line = lines[tax_line_idx-1].strip()
                if is_valid_company_name(prev_line):
                    company_name = prev_line
                    if ':' in company_name:
                        company_name = company_name.split(':', 1)[1].strip()
            if not company_name:
                for line in lines[:10]:
                    l = line.strip()
                    if is_valid_company_name(l):
                        company_name = l
                        if ':' in company_name:
                            company_name = company_name.split(':', 1)[1].strip()
                        break
            if not company_name and tax_line_idx and tax_line_idx > 0:
                prev_line = lines[tax_line_idx-1].strip()
                if is_valid_company_name(prev_line):
                    company_name = prev_line
                    if ':' in company_name:
                        company_name = company_name.split(':', 1)[1].strip()
            # Trích xuất thuế suất
            tax_rate_val = 0.0
            tax_rate_aliases = [normalize_fuzzy(a) for a in default_config.get('tax_rate', [])]
            for line in lines:
                norm_line = normalize_fuzzy(line)
                if any(alias in norm_line for alias in tax_rate_aliases):
                    m = re.search(r'(\d{1,2}) ?%', line)
                    if m:
                        tax_rate_val = float(m.group(1)) / 100
                        break
            data = {
                'date': date,
                'tax_code': tax_code,
                'invoice_number': invoice_number_val,
                'company_name': company_name,
                'tax_rate': float(tax_rate_val) if tax_rate_val else 0.0
            }
            if not data['tax_code'] or not data['invoice_number']:
                errors.append(f"Missing required fields in {pdf_path}: tax_code or invoice_number")
            # Trích xuất bảng
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if not tables:
                    errors.append(f"No tables found in {pdf_path}")
                    continue
                for table_idx, table in enumerate(tables):
                    header_row_idx = None
                    for idx, row in enumerate(table):
                        if row and any(h for h in row if h and ('STT' in h or 'No.' in h)) and any(h for h in row if h and ('Tên hàng' in h or 'Description' in h)):
                            header_row_idx = idx
                            break
                    if header_row_idx is None:
                        continue
                    headers = table[header_row_idx]
                    next_row_is_subheader = False
                    if header_row_idx+1 < len(table):
                        next_row = table[header_row_idx+1]
                        if next_row and sum(1 for h in next_row if h and ('%' in h or 'thuế' in h.lower())) >= 1:
                            next_row_is_subheader = True
                    norm_headers = [normalize_header(h) for h in headers]
                    stt_index = next((i for i, h in enumerate(norm_headers) if h and ('stt' in h or 'no' in h)), None)
                    data_start_idx = header_row_idx + 2 if next_row_is_subheader else header_row_idx + 1
                    for row_idx, row in enumerate(table[data_start_idx:], start=data_start_idx):
                        if row == None or stt_index is None or not row[stt_index] or not row[stt_index].isdigit() or row[stt_index] == '0':
                            continue
                        row_data = data.copy()
                        for field, aliases in default_config.get('table_columns', {}).items():
                            found = False
                            for i, header in enumerate(headers):
                                norm_h = normalize_header(header)
                                norm_h_fuzzy = normalize_fuzzy(header)
                                alias_match = False
                                for alias in aliases:
                                    norm_alias_fuzzy = normalize_fuzzy(alias)
                                    if norm_alias_fuzzy in norm_h_fuzzy or norm_h_fuzzy in norm_alias_fuzzy:
                                        alias_match = True
                                        break
                                is_tax_rate_col = False
                                is_tax_amount_col = False
                                if field == 'tax_rate':
                                    if '%' in norm_h_fuzzy or 'thue' in norm_h_fuzzy or 'vat' in norm_h_fuzzy or 'tax' in norm_h_fuzzy or 'gtgt' in norm_h_fuzzy:
                                        is_tax_rate_col = True
                                if field == 'tax_amount':
                                    if 'tien thue' in norm_h_fuzzy or 'vat amount' in norm_h_fuzzy:
                                        is_tax_amount_col = True
                                if next_row_is_subheader and i < len(table[header_row_idx+1]):
                                    subheader_val = table[header_row_idx+1][i] or ''
                                    norm_subheader_fuzzy = normalize_fuzzy(subheader_val)
                                    if field == 'tax_rate' and ('%' in norm_subheader_fuzzy or 'thue' in norm_subheader_fuzzy or 'vat' in norm_subheader_fuzzy or 'tax' in norm_subheader_fuzzy or 'gtgt' in norm_subheader_fuzzy):
                                        val = row[i] or ''
                                        if isinstance(val, str) and '%' in val:
                                            try:
                                                row_data[field] = float(val.replace('%','').replace(',','.').strip())/100
                                            except Exception:
                                                row_data[field] = data['tax_rate']
                                        else:
                                            try:
                                                row_data[field] = float(val.replace(',','.').strip()) if val else data['tax_rate']
                                            except Exception:
                                                row_data[field] = data['tax_rate']
                                        found = True
                                        break
                                    elif field == 'tax_amount' and ('tien thue' in norm_subheader_fuzzy or 'vat amount' in norm_subheader_fuzzy):
                                        val = row[i] or ''
                                        try:
                                            row_data[field] = parse_number(val)
                                        except Exception:
                                            row_data[field] = 0.0
                                        found = True
                                        break
                                    elif field not in ['tax_rate', 'tax_amount']:
                                        if alias_match:
                                            row_data[field] = row[i] or ''
                                            found = True
                                            break
                                elif alias_match or (field == 'tax_rate' and is_tax_rate_col) or (field == 'tax_amount' and is_tax_amount_col):
                                    row_data[field] = row[i] or ''
                                    found = True
                                    break
                            if not found:
                                row_data[field] = ''
                        try:
                            if isinstance(row_data.get('tax_rate'), str):
                                val = row_data.get('tax_rate','')
                                if '%' in val:
                                    row_data['tax_rate'] = float(val.replace('%','').replace(',','.').strip())/100
                                elif val.strip() == '' or val.strip() == '%':
                                    row_data['tax_rate'] = data['tax_rate']
                                else:
                                    row_data['tax_rate'] = float(val.replace(',','.').strip())
                        except Exception:
                            row_data['tax_rate'] = data['tax_rate']
                        def is_col_index(val):
                            v = str(val).strip()
                            return (v.isdigit() or (len(v) == 1 and v.isalpha()))
                        num_fields = ['quantity', 'unit_price', 'subtotal']
                        if all(is_col_index(row_data.get(f, '')) for f in num_fields) or (row_data.get('item_name', '').strip().isdigit()):
                            continue
                        main_fields = ['item_name', 'unit', 'quantity', 'unit_price', 'subtotal']
                        if all((not row_data.get(f) or str(row_data.get(f)).strip() in ('', '0', '0.0')) for f in main_fields):
                            continue
                        try:
                            row_data['quantity'] = parse_number(row_data.get('quantity', '0'))
                            row_data['unit_price'] = parse_number(row_data.get('unit_price', '0'))
                            row_data['subtotal'] = parse_number(row_data.get('subtotal', '0'))
                            if not row_data['subtotal']:
                                row_data['subtotal'] = row_data['quantity'] * row_data['unit_price']
                            # Làm tròn thành tiền tới chữ số hàng đơn vị
                            row_data['subtotal'] = round(row_data['subtotal'])
                            
                            tax_rate = row_data.get('tax_rate')
                            if tax_rate in (None, '', 0, 0.0):
                                tax_rate = data.get('tax_rate', 0.0)
                            row_data['tax_rate'] = tax_rate
                            row_data['tax_amount'] = row_data['subtotal'] * tax_rate
                            # Làm tròn tiền thuế tới chữ số hàng đơn vị
                            row_data['tax_amount'] = round(row_data['tax_amount'])
                            
                            row_data['total'] = row_data['subtotal'] + row_data['tax_amount']
                            # Làm tròn tổng tiền tới chữ số hàng đơn vị
                            row_data['total'] = round(row_data['total'])
                            
                            row_data['category'] = ''
                            data_list.append(row_data)
                        except Exception as e:
                            errors.append(f"Invalid data in table row {row_idx}: {e}")
            return data_list, errors
    except Exception as e:
        return [], [f"Failed to process {pdf_path}: {e}"] 

