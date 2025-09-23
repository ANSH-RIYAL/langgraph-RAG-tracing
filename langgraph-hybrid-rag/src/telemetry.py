import time
from contextlib import contextmanager


@contextmanager
def log_step(step: str, logger=print, **fields):
    start = time.time()
    try:
        yield
    finally:
        duration_ms = int((time.time() - start) * 1000)
        record = {"step": step, "duration_ms": duration_ms}
        record.update(fields)
        logger(record)




