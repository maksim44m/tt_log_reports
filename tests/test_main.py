import sys
from pathlib import Path
import argparse
import pytest
sys.path.append(str(Path(__file__).parent.parent))

from reporter import BaseReport
from main import worker, cmd_parser


TEST_DIR = Path(__file__).parent.absolute()


def test_worker():
    args = argparse.Namespace(
        logs=['tests/test.txt'],
        report='handlers'
    )
    
    report = worker(args)
    
    assert isinstance(report, BaseReport)
    assert hasattr(report, 'merge')
    assert hasattr(report, 'run')
    assert hasattr(report, 'print_report')
    assert callable(report.merge)
    assert callable(report.run)
    assert callable(report.print_report)


def test_worker_multiple_files():
    """Тест на обработку нескольких файлов"""
    args = argparse.Namespace(
        logs=['tests/test.txt', 'tests/test.txt'],
        report='handlers'
    )
    
    report = worker(args)
    assert isinstance(report, BaseReport)


def test_worker_invalid_files():
    """Тест на обработку несуществующего файла"""
    args = argparse.Namespace(
        logs=['tests/.txt'],
        report='handlers'
    )
    
    with pytest.raises(ValueError) as exc_info:
        worker(args)
    assert 'Нет успешно обработанных файлов' in str(exc_info.value)


def test_worker_mixed_files():
    """Тест на обработку смешанных файлов"""
    args = argparse.Namespace(
        logs=['tests/test.txt', 'tests/not_exists.txt'],
        report='handlers'
    )
    
    report = worker(args)
    assert isinstance(report, BaseReport)


def test_cmd_parser():
    """Тест на парсинг аргументов командной строки"""
    sys.argv = ['main.py', 'test.txt', '--report', 'handlers']
    args = cmd_parser()
    assert args.logs == ['test.txt']
    assert args.report == 'handlers'


def test_cmd_parser_invalid_report():
    """Тест на парсинг несуществующего отчета"""
    sys.argv = ['main.py', 'test.txt', '--report', 'invalid']
    with pytest.raises(SystemExit):
        cmd_parser()
