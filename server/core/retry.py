"""
core/retry.py
--------------
외부 API(카카오, OpenAI 등) 호출처럼 일시적으로 실패할 수 있는 함수에 붙이는
지수 백오프 재시도 데코레이터.
"""
import functools
import time

from core.logger import get_logger

logger = get_logger(__name__)


def retry_with_backoff(*, retries: int = 3, base_delay: float = 0.5, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == retries:
                        logger.error(
                            "%s 재시도 %d회 모두 실패: %s", func.__name__, retries, exc
                        )
                        raise
                    logger.warning(
                        "%s 실패(%d/%d회), %.1f초 후 재시도: %s",
                        func.__name__, attempt, retries, delay, exc,
                    )
                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator