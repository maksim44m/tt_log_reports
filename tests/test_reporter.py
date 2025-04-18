import sys
from pathlib import Path
import pytest
sys.path.append(str(Path(__file__).parent.parent))

from reporter import HandlersReport, ReportFactory, BaseReport, LogParser


TEST_DIR = Path(__file__).parent.absolute()


def test_log_parser():
    """Тест на парсинг строки лога"""
    parser = LogParser()
    
    # Валидная строка
    line = '2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]'
    result = parser.parse_line(line)
    assert result['timestamp'] == '2025-03-28 12:44:46,000'
    assert result['level'] == 'INFO'
    assert result['module'] == 'django.request'
    assert result['message'] == 'GET /api/v1/reviews/ 204 OK [192.168.1.59]'
    
    # Невалидная строка
    result = parser.parse_line('invalid log line')
    assert result == {}


def test_handlers_report_merge():
    """Тест на слияние отчетов"""
    report1 = HandlersReport()
    report1.count['/api/v1/users']['INFO'] = 5
    report1.count['/api/v1/products']['ERROR'] = 2

    report2 = HandlersReport()
    report2.count['/api/v1/users']['WARNING'] = 3
    report2.count['/api/v1/cart']['INFO'] = 1

    report1.merge([report2])

    assert report1.count['/api/v1/users']['INFO'] == 5
    assert report1.count['/api/v1/users']['WARNING'] == 3
    assert report1.count['/api/v1/products']['ERROR'] == 2
    assert report1.count['/api/v1/cart']['INFO'] == 1


def test_handlers_report_merge_invalid_type():
    class TestReport(BaseReport):
        def merge(self, others):
            pass

        def run(self, path):
            return self

        def print_report(self):
            pass
    
    report1 = HandlersReport()
    report2 = TestReport()  # Неправильный тип
    
    with pytest.raises(TypeError) as exc_info:
        report1.merge([report2])
    assert 'Ожидается HandlersReport' in str(exc_info.value)


def test_handlers_report_run():
    """Тест на запуск формирования отчета"""
    report = HandlersReport()
    result = report.run(TEST_DIR / 'test.txt')

    assert isinstance(result, HandlersReport)
    assert report.count['/api/v1/reviews/']['INFO'] == 2
    assert report.count['/admin/dashboard/']['INFO'] == 1
    assert report.count['/api/v1/users/']['INFO'] == 1
    assert report.count['/api/v1/cart/']['INFO'] == 1
    assert report.count['/api/v1/products/']['INFO'] == 1
    assert report.count['/api/v1/support/']['INFO'] == 1
    assert report.count['/api/v1/support/']['ERROR'] == 2
    assert report.count['/admin/dashboard/']['ERROR'] == 1
    assert report.count['/api/v1/auth/login/']['INFO'] == 1
    assert report.count['/admin/login/']['INFO'] == 1


def test_handlers_report_run_invalid_file():
    """Тест на запуск формирования отчета для несуществующего файла"""
    report = HandlersReport()
    with pytest.raises(Exception) as exc_info:
        report.run(TEST_DIR / 'nonexistent.txt')
    assert not report.count
    assert 'Ошибка при чтении файла' in str(exc_info.value)


def test_handlers_report_print(capsys):
    """Тест на вывод отчета"""
    report = HandlersReport()
    report.count['/api/v1/users']['INFO'] = 5
    report.count['/api/v1/products']['ERROR'] = 2
    report.count['/api/v1/cart']['INFO'] = 1

    report.print_report()
    captured = capsys.readouterr()

    assert 'Total requests: 8' in captured.out
    assert '/api/v1/users' in captured.out
    assert '/api/v1/products' in captured.out
    assert '/api/v1/cart' in captured.out
    assert 'INFO' in captured.out
    assert 'ERROR' in captured.out
    assert 'WARNING' in captured.out
    assert 'DEBUG' in captured.out
    assert 'CRITICAL' in captured.out


def test_report_factory():
    """Тест на создание объекта отчета заданного типа"""
    report = ReportFactory.get_report('handlers')
    assert isinstance(report, HandlersReport)


def test_report_factory_invalid_type():
    """Тест на создание отчета с неизвестным типом"""
    with pytest.raises(ValueError) as exc_info:
        ReportFactory.get_report('invalid')
    assert 'Неизвестный тип отчета' in str(exc_info.value)





