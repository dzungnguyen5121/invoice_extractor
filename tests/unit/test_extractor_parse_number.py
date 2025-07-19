import pytest
from src.extractor import parse_number

def test_parse_number_basic():
    assert parse_number("1234") == 1234.0
    assert parse_number("1.234,56") == 1234.56
    assert parse_number("2,5") == 2.5
    assert parse_number("1000") == 1000.0
    assert parse_number("0") == 0.0
    assert parse_number("-123") == -123.0
    assert parse_number("-1.234,56") == -1234.56

def test_parse_number_empty_and_none():
    assert parse_number("") == 0.0
    assert parse_number(None) == 0.0

def test_parse_number_invalid():
    assert parse_number("abc") == 0.0
    assert parse_number("12a34") == 0.0
    assert parse_number("1,2,3") == 0.0
    assert parse_number("1.2.3") == 0.0
    assert parse_number("=123") == 0.0
    assert parse_number("12=3") == 0.0
    assert parse_number("1.234.567,89abc") == 0.0
    assert parse_number("12@34,56") == 0.0
    assert parse_number("-0") == 0.0
    assert parse_number("0.0") == 0.0
    assert parse_number("0,0") == 0.0
    # Các trường hợp lẫn lộn dấu phân cách, phải trả về 0.0
    assert parse_number("1.234,567.89") == 0.0
    assert parse_number("1,234.567,89") == 0.0

def test_parse_number_large_and_small():
    assert parse_number("9999999999") == 9999999999.0
    assert parse_number("-9999999999") == -9999999999.0
    assert parse_number("0.0001") == 0.0001
    assert parse_number("-0.0001") == -0.0001

def test_parse_number_grouping_and_decimal():
    # Kiểu Việt Nam
    assert parse_number("1.000.000") == 1000000.0
    assert parse_number("1.000.000,99") == 1000000.99
    assert parse_number("1.234.567,89") == 1234567.89
    assert parse_number("1 234,56") == 1234.56
    # Kiểu quốc tế
    assert parse_number("1,150,000") == 1150000.0
    assert parse_number("1,234,567.89") == 1234567.89
    assert parse_number("1,000,000.99") == 1000000.99
    assert parse_number("1,000.99") == 1000.99
    # Trường hợp chỉ có dấu ngăn cách ngàn
    assert parse_number("1.000.000") == 1000000.0
    assert parse_number("1,150,000") == 1150000.0 