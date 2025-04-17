import re
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
from pathlib import Path
from typing import List


class BaseReport(ABC):
    @abstractmethod
    def merge(self, others: List['BaseReport']) -> None:
        pass

    @abstractmethod
    def run(self, path: Path) -> 'BaseReport':
        pass

    @abstractmethod
    def print_report(self) -> None:
        pass


class HandlersReport(BaseReport):
    def __init__(self):
        # словарь словарей, где ключ - ручка, значение - словарь с ключами - уровень и значениями - количество
        self.count: defaultdict[str, Counter[str]] = defaultdict(Counter)

        self.match_pattern = re.compile(
            r'^'  # время - уровень - модуль - сообщение
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s+'
            r'(?P<level>[A-Z]+)\s+'
            r'(?P<module>[\w\.]+):\s+'
            r'(?P<message>.*)'
            r'$'
        )

    def merge(self, others: List[BaseReport]) -> None:
        for report in others:
            if not isinstance(report, HandlersReport):
                raise TypeError(f'Ожидается HandlersReport, получен {type(report)}')
            for handler, count in report.count.items():
                self.count[handler].update(count)

    def run(self, path: Path) -> BaseReport:
        handle_pattern = re.compile(r'/\S+')  # ручка
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    match = self.match_pattern.match(line)
                    if not match:
                        continue
                    
                    level = match.group('level')
                    message = match.group('message')
                    
                    handle = handle_pattern.search(message)
                    if handle:
                        self.count[handle.group(0)][level] += 1
        except Exception as e:
            print(f'Ошибка при чтении файла {path}: {e}')
        
        return self
    
    def print_report(self) -> None:
        total_levels_count = Counter()
        for levels in self.count.values():
            total_levels_count.update(levels)

        total_requests = sum(sum(levels.values()) for levels in self.count.values())
        static_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        max_len_handler = max(len(h) for h in self.count.keys())

        print(f'Total requests: {total_requests}')
        print(f'{"":<{max_len_handler}}{"".join([f"{lvl:>10}" for lvl in static_levels])}')
        for handle, levels in sorted(self.count.items()):
            line = f'{handle:<{max_len_handler}}'
            for level in static_levels:
                line += f'{levels[level]:>10}'
            print(line)
        print(f"{'':<{max_len_handler}}{''.join([f'{total_levels_count[lvl]:>10}' for lvl in static_levels])}")


class ReportFactory:
    _reports = {
        'handlers': HandlersReport,
    }

    @classmethod
    def get_report(cls, report_type: str) -> BaseReport:
        if report_type not in ReportFactory._reports:
            raise ValueError(f'Неизвестный тип отчета: {report_type}')
        return cls._reports[report_type]()

