from __future__ import annotations

import statistics
from typing import Any, Dict

from sortedcontainers import SortedList  # type:ignore


class Histogram:
    width_: int
    hist_: Dict[int, int]
    all_measurements_: SortedList

    max_count_: int = 0

    def __init__(self, values_col_name: str, width: int) -> None:
        self.width_ = width
        self.values_col_name_ = values_col_name
        self.hist_ = dict()
        self.all_measurements_ = SortedList()

    def add(self, value: Any) -> None:

        index = int(value / self.width_) if isinstance(value, int) else value
        count = self.hist_.get(index, 0) + 1
        self.hist_[index] = count
        self.max_count_ = max(self.max_count_, count)
        self.all_measurements_.add(value)

    def _num_bars(self, count: int) -> int:
        # 50 for max
        return int(43 * count / self.max_count_) + 1


    def is_empty(self) -> bool:
        return len(self.all_measurements_) == 0

    def to_string(self, **kwargs) -> str:
        res: str = ''

        if self.is_empty():
            return res

        is_int: bool = isinstance(self.all_measurements_[0], int)
        col1_width: int = kwargs.get("col1_width", 16)
        keys = [k for k in self.hist_.keys()]
        keys.sort()

        res += ("\n" + "-" * 70)
        if is_int:
            res += '\n' + (f'{self.values_col_name_:>{col1_width}s}{"Count":>8s}')
        else:
            res += '\n' + (f'{self.values_col_name_:{col1_width}s}{"Count":>8s}')
        res += '\n' + ("-" * 70)

        for idx in keys:
            count = self.hist_[idx]
            if is_int:
                res += '\n' + (
                    f"{(idx * self.width_):{col1_width},d}{count:8,d}  {'|' * self._num_bars(count)}"
                )
            else:
                res += '\n' + (
                    f"{str(idx):{col1_width}s}{count:>8,d}  {'|' * self._num_bars(count)}"
                )
        res += '\n' + ("-" * 70)
        res += '\n' + (f"Total Measurements: {len(self.all_measurements_):,}")
        if is_int:
            res += '\n' + (
                f"Min: {min(self.all_measurements_):,}"
                + f" Mean: {int(statistics.mean(self.all_measurements_)):,}"
                + f" Median: {int(statistics.median(self.all_measurements_)):,}"
                + f" Max: {max(self.all_measurements_):,}"
            )

        return res

    def print(self, **kwargs) -> None:
        print(self.to_string(**kwargs))




if __name__ == "__main__":
    import sys

    file = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    hist = Histogram(f"{file} order submit->ack (millis)", width)
    with open(file) as fl:
        for line in fl:
            val = int(line)
            hist.add(val)

    hist.print()
