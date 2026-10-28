from contextlib import contextmanager
from time import perf_counter
from collections.abc import Callable, Iterator


@contextmanager
def measure_duration(
    on_complete: Callable[[float], None],
) -> Iterator[None]:
    started = perf_counter()

    try:
        yield
    finally:
        duration_ms = (perf_counter() - started) * 1000
        on_complete(duration_ms)