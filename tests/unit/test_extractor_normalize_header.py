import unittest
from src.extractor import normalize_header

class TestNormalizeHeader(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(normalize_header('Số lượng'), 'số lượng')
        self.assertEqual(normalize_header('Đơn giá'), 'đơn giá')
        self.assertEqual(normalize_header('Thành tiền'), 'thành tiền')

    def test_with_newline_and_spaces(self):
        self.assertEqual(normalize_header('Số\nLượng'), 'số lượng')
        self.assertEqual(normalize_header('  Đơn   giá  '), 'đơn giá')

    def test_with_special_chars(self):
        self.assertEqual(normalize_header('Thành tiền:'), 'thành tiền')
        self.assertEqual(normalize_header('(Số lượng)'), 'số lượng')
        self.assertEqual(normalize_header('Đơn giá.'), 'đơn giá')
        self.assertEqual(normalize_header('Thành tiền:'), 'thành tiền')

    def test_empty_and_none(self):
        self.assertEqual(normalize_header(''), '')
        self.assertEqual(normalize_header(None), '')

    def test_multiple_spaces(self):
        self.assertEqual(normalize_header('Số    lượng'), 'số lượng')
        self.assertEqual(normalize_header('  Đơn   giá  '), 'đơn giá')

if __name__ == '__main__':
    unittest.main() 