# $env:PYTHONPATH="D:\rat_la_tu_dong\rat_la_tu_dong"; pytest tests/integration/extractor/test_extract_pdf.py


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

import json
import pytest
from src.extractor import extract_data_from_pdf, load_config

TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, "data")
CONFIG_PATH = os.path.abspath(os.path.join(TEST_DIR, '..', '..', '..', 'config.json'))
UPLOADS_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', '..', '..', 'uploads'))

@pytest.mark.parametrize("case_file", [
    "expected_HD_299_7-7.json"
])
def test_extract_pdf(case_file):
    # Đọc dữ liệu mong đợi
    with open(os.path.join(DATA_DIR, case_file), encoding="utf-8") as f:
        data = json.load(f)
    pdf_path = os.path.join(UPLOADS_DIR, data["pdf"])
    expected = data["expected"]
    config = load_config(CONFIG_PATH)
    result, errors = extract_data_from_pdf(pdf_path, config)
    assert not errors, f"Errors: {errors}"
    # So sánh từng trường, từng dòng
    assert len(result) == len(expected), f"Số dòng kết quả ({len(result)}) khác mong đợi ({len(expected)})"
    for exp, res in zip(expected, result):
        for k in exp:
            # So sánh số thực với sai số nhỏ
            if isinstance(exp[k], float):
                assert abs(exp[k] - float(res.get(k, 0))) < 1e-3, f"Field {k}: expected {exp[k]}, got {res.get(k)}"
            else:
                assert exp[k] == res.get(k), f"Field {k}: expected {exp[k]}, got {res.get(k)}" 