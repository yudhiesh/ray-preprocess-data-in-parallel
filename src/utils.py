from functools import wraps
import json
import logging
from time import time

import aiofiles

from src.constants import ROOT_DIR

logging.basicConfig(
    format="%(process)d-%(levelname)s-%(message)s",
    level=logging.INFO,
)


def timer(file_path: str, to_save: bool):
    def timing(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            t1 = time()
            result = func(*args, **kwargs)
            total_time = time() - t1
            logging.info(f"Function {func.__name__!r} executed in {total_time:.4f}s")
            time_results = ROOT_DIR / file_path
            if to_save:
                with open(time_results) as json_file:
                    json_decoded = (
                        {f"{func.__name__}": total_time}
                        if json_file == ""
                        else json.load(json_file)
                    )
                json_decoded[f"{func.__name__}"] = total_time
                with open(time_results, "w") as json_file:
                    json.dump(json_decoded, json_file)

            return result

        return wrap

    return timing


def async_timer(file_path: str, to_save: bool):
    def timing(func):
        async def process(func, *args, **params):
            return await func(*args, **params)

        async def helper(*args, **params):
            start = time()
            result = await process(func, *args, **params)
            total_time = time() - start
            logging.info(
                f"Function {func.__name__!r} executed in {(total_time):.4f}s",
            )
            time_results_file = ROOT_DIR / file_path
            if to_save:
                async with aiofiles.open(time_results_file, "r") as json_file:
                    json_object = await json_file.read()
                    json_decoded = (
                        {f"{func.__name__}": total_time}
                        if json_object == ""
                        else json.loads(json_object)
                    )
                json_decoded[f"{func.__name__}"] = total_time
                async with aiofiles.open(time_results_file, "w") as json_file:
                    await json_file.write(json.dumps(json_decoded))

            return result

        return helper

    return timing
