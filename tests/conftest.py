"""Fixtures pytest."""

from __future__ import annotations

from typing import Dict, List, Tuple

import pytest


@pytest.fixture(scope="session")
def benchmark_results() -> Dict[str, List[Tuple[int, float]]]:
    return {"prim": [], "solver": [], "prim_scaling": []}


def pytest_configure(config):
    config.addinivalue_line("markers", "performance: testy pomiaru czasu (wolniejsze)")
