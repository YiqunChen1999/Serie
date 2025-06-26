
import sys
import inspect
import os.path as osp
from time import sleep

import openai
import tabulate
from openai import OpenAI

from serie.utils.logging import create_logger


logger = create_logger(__name__)


def get_class_config_file_path(cls, file_name: str = ""):
    json_path = get_class_file_path(cls)
    json_path = json_path.replace("serie/serie", "serie/configs")
    if not osp.exists(json_path):
        json_path = json_path.replace(".py", ".json")
    if file_name:
        json_path = osp.join(osp.dirname(json_path), file_name)
    return json_path


def get_class_file_path(cls):
    module = sys.modules[cls.__module__]
    file_path = inspect.getfile(module)
    return file_path


def wait_batch_task(client: OpenAI,
                    batch: openai.types.Batch,
                    interval: float = 10):
    while True:
        sleep(interval)
        job = client.batches.retrieve(batch.id)
        if job.status in ("validating", "in_progress", "finalizing"):
            logger.info(f"Completion status: {job.status}, "
                        f"batch id: {batch.id}")
            continue
        else:
            logger.info(
                f"Complete batches task exists with status: {job.status}.\n"
                f"Details: {job}")
            break
    return client.batches.retrieve(batch.id)


def batch_task_success(batch: openai.types.Batch):
    return batch.status in ("completed",)


def _wrap_text_to_colwidths(list_of_lists: list[list],
                            colwidths: list[int | None],
                            numparses: list[bool] | bool = True,
                            missing_value: str = ""):
    if len(list_of_lists):
        num_cols = len(list_of_lists[0])
    else:
        num_cols = 0
    numparses = tabulate._expand_iterable(numparses, num_cols, True)  # type: ignore # noqa: E501

    result = []

    for row in list_of_lists:
        new_row = []
        assert isinstance(numparses, list), (
            "Each row in list_of_lists must be a list, "
            f"got {type(row)} instead."
        )
        for cell, width, numparse in zip(row, colwidths, numparses):
            if tabulate._isnumber(cell) and numparse:  # type: ignore # noqa: E501
                new_row.append(cell)
                continue

            if width is not None:
                wrapper = tabulate._CustomTextWrap(width=width)  # type: ignore # noqa: E501
                # Cast based on our internal type handling. Any future custom
                # formatting of types (such as datetimes) may need to be more
                # explicit than just `str` of the object. Also doesn't work for
                # custom floatfmt/intfmt, nor with any missing/blank cells.
                casted_cell = (
                    str(cell)
                    if tabulate._isnumber(cell)  # type: ignore # noqa: E501
                    else (  # FIX the None type error
                        tabulate._type(cell, numparse)(cell)  # type: ignore # noqa: E501
                        if cell else missing_value
                    )
                )
                wrapped = [
                    "\n".join(wrapper.wrap(line))
                    for line in casted_cell.splitlines()
                    if line.strip() != ""
                ]
                new_row.append("\n".join(wrapped))
            else:
                new_row.append(cell)
        result.append(new_row)

    return result


def apply_patch():
    apply_tabulate_patch()


def apply_tabulate_patch():
    """
    Apply a patch to the tabulate library to handle text wrapping correctly.

    This function modifies the tabulate library's internal behavior to ensure
    that text wrapping works as expected, especially for cells that are None.
    It replaces the original `_wrap_text_to_colwidths` function with a custom
    implementation that handles None values and text wrapping more robustly.
    """
    tabulate._wrap_text_to_colwidths = _wrap_text_to_colwidths  # type: ignore # noqa: E501

