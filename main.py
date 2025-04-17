import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from reporter import ReportFactory, BaseReport


BASE_DIR = Path(__file__).parent.absolute()


def worker(args: argparse.Namespace) -> BaseReport:
    paths = [BASE_DIR / path for path in args.logs]
    report_type = args.report
    report = ReportFactory.get_report(report_type)

    reports = []
    with ProcessPoolExecutor() as executor:
        futures_to_path = {
            executor.submit(report.run, p): p for p in paths
        }

        for future in as_completed(futures_to_path):
            path = futures_to_path[future]
            try:
                result = future.result()
            except Exception as e:
                print(f'Ошибка при обработке {path}: {e}')
            else:
                reports.append(result)

    if not reports:
        raise ValueError('Нет успешно обработанных файлов')

    final_report = reports[0]
    final_report.merge(reports[1:])

    return final_report

def cmd_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Запускает формирование отчетов по логам'
    )
    parser.add_argument(
        'logs', 
        nargs='+',
        help='Пути к лог‑файлам (один или несколько)'
    )
    parser.add_argument(
        '--report',
        required=True,
        choices=ReportFactory._reports.keys(),
        help=f'Тип отчета ({", ".join(ReportFactory._reports.keys())})'
    )
    return parser.parse_args()


def main() -> None:
    report = worker(cmd_parser())
    report.print_report()


if __name__ == '__main__':
    main()

