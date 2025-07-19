import unittest
from src.extractor import normalize_fuzzy

class TestNormalizeFuzzy(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(normalize_fuzzy('Số lượng'), 'so luong')
        self.assertEqual(normalize_fuzzy('Đơn giá'), 'don gia')
        self.assertEqual(normalize_fuzzy('Thành tiền'), 'thanh tien')

    def test_with_diacritics_and_special_chars(self):
        self.assertEqual(normalize_fuzzy('Số\nLượng:'), 'so luong')
        self.assertEqual(normalize_fuzzy('(Đơn giá).'), 'don gia')
        self.assertEqual(normalize_fuzzy('Thành tiền:'), 'thanh tien')
        self.assertEqual(normalize_fuzzy('Tổng cộng (VNĐ):'), 'tong cong vnd')

    def test_with_percent(self):
        self.assertEqual(normalize_fuzzy('Thuế suất %'), 'thue suat %')
        self.assertEqual(normalize_fuzzy('VAT (%)'), 'vat %')
        self.assertEqual(normalize_fuzzy('10%'), '10 %')

    def test_empty_and_none(self):
        self.assertEqual(normalize_fuzzy(''), '')
        self.assertEqual(normalize_fuzzy(None), '')

    def test_numbers_and_letters(self):
        self.assertEqual(normalize_fuzzy('123 ABC'), '123 abc')
        self.assertEqual(normalize_fuzzy('Số 1, số 2.'), 'so 1 so 2')

    def test_multiple_spaces(self):
        self.assertEqual(normalize_fuzzy('Số    lượng'), 'so luong')
        self.assertEqual(normalize_fuzzy('  Đơn   giá  '), 'don gia')

if __name__ == '__main__':
    unittest.main() 