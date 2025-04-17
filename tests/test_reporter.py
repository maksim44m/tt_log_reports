import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from reporter import HandlersReport, ReportFactory, BaseReport


TEST_DIR = Path(__file__).parent.absolute()


def test_handlers_report_merge():
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


def test_handlers_report_run():
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


def test_handlers_report_print(capsys):
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


def test_report_factory():
    report = ReportFactory.get_report('handlers')
    assert isinstance(report, HandlersReport)


def test_report_factory_invalid_type():
    try:
        ReportFactory.get_report('invalid')
        assert False, 'Должно быть исключение'
    except ValueError as e:
        assert 'Неизвестный тип отчета' in str(e)





