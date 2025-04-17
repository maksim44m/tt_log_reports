import sys
from pathlib import Path
import argparse
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


def test_cmd_parser():
    sys.argv = ['main.py', 'test.txt', '--report', 'handlers']
    args = cmd_parser()
    assert args.logs == ['test.txt']
    assert args.report == 'handlers'
