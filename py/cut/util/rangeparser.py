import logging
import re
from typing import Tuple

LOG = logging.getLogger(__name__)


class InvalidFieldRangeValueError(Exception):
    pass


def normalize_list_ranges(field_ranges) -> list[Tuple]:
    r = []
    for field_range in field_ranges:
        if " " in field_range:
            indices = field_range.split()
            r.append(list(**indices))

        elif "-" in field_range:
            max_fields = 1 << 16
            indices = field_range.split("-")
            if len(indices) > 2:
                raise InvalidFieldRangeValueError(
                    f"cut: invalid field range '{field_range}'"
                )
            start, end = 1, max_fields
            if len(indices[0]):
                start = int(indices[0])
            if len(indices[1]):
                end = int(indices[1])
            if start > end:
                raise InvalidFieldRangeValueError("invalid decreasing range")
            r.append([start, end])

        elif re.search(r"\d+", field_range):
            try:
                v = int(field_range)
                r.append([v, v])
            except ValueError as e:
                LOG.debug(e)
                raise InvalidFieldRangeValueError(
                    f"cut: invalid field value '{field_range}'"
                )

    LOG.debug("The normalized interval: %s", r)
    intervals = merge_overlapping_intervals(r)
    LOG.debug("The ranges to print : %s", intervals)
    return intervals


def merge_overlapping_intervals(x):
    """Merge overlapping intervals without preserving order."""
    x.sort(key=lambda i: i[0])

    ans = []
    ans.append(x[0])

    for cur in x[1:]:
        last = ans[-1]

        if cur[0] <= last[1]:
            new_end = max(last[1], cur[1])
            last[1] = new_end
        else:
            ans.append(cur)

    return ans


def complement_ranges(input_ranges):
    input_ranges.sort(key=lambda i: i[0])
    max_field_index = 1 << 16
    C = []
    current = 1
    for start, end in input_ranges:
        if start > current:
            C.append([current, start - 1])
        if end < max_field_index:
            current = end + 1
        if [start, end] == input_ranges[-1]:
            C.append([end + 1, max_field_index])
    return C
