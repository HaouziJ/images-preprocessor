import time
from functools import wraps
from logging import Logger
from configparser import SectionProxy
import os

def retry(exceptions, tries: int = 2, delay: int = 3, backoff: int = 2, logger: Logger = None):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        exceptions: The exception to check. may be a tuple of
            exceptions to check.
        tries: Number of times to try (not retry) before giving up.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier (e.g. value of 2 will double the delay
            each retry).
        logger: Logger to use. If None, print.
    """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = '{}, Retrying in {} seconds...'.format(e, mdelay)
                    if logger:
                        logger.info(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


def init_directory_structure(resources: SectionProxy, logger: Logger):
    for directory_path in resources:
        directory = resources[directory_path]
        if not os.path.exists(directory):
            logger.info('Creating directory {}...'.format(directory))
            os.makedirs(directory)
        else:
            logger.warning('[DONE] Directory {} already exists'.format(directory))
