import json
from pathlib import Path

import pytest

from parser.docx_parser import parse_from_docx

DATA = Path(__file__).parent / "data"


def assert_equal(actual, expected, path="$"):
    """Сравнивает рекурсивно, при первом расхождении показывает путь."""
    if type(actual) is not type(expected):
        raise AssertionError(
            f"{path}: тип {type(actual).__name__} != {type(expected).__name__}"
        )
    if isinstance(actual, dict):
        if set(actual) != set(expected):
            missing = set(expected) - set(actual)
            extra = set(actual) - set(expected)
            raise AssertionError(f"{path}: ключи — missing={missing}, extra={extra}")
        for k in actual:
            assert_equal(actual[k], expected[k], f"{path}.{k}")
    elif isinstance(actual, list):
        if len(actual) != len(expected):
            raise AssertionError(f"{path}: длина {len(actual)} != {len(expected)}")
        for i, (a, e) in enumerate(zip(actual, expected)):
            assert_equal(a, e, f"{path}[{i}]")
    else:
        if actual != expected:
            raise AssertionError(f"{path}: {actual!r} != {expected!r}")


@pytest.mark.parametrize(
    "docx_path",
    sorted(DATA.glob("*.docx")),
    ids=lambda p: p.stem,
)
def test_parser(docx_path):
    expected_path = docx_path.with_suffix(".expected.json")
    if not expected_path.exists():
        pytest.fail(f"Нет эталона для {docx_path.name}. Сгенерируй и проверь руками.")

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    actual = parse_from_docx(docx_path)

    assert_equal(actual, expected)