#!/usr/bin/env python3
from __future__ import annotations

import datetime
import time
from enum import Enum
from typing import Optional

NanosT = int

HourPerDay = 24
MinPerHour = 60

SecPerMin = 60
SecPerHour = SecPerMin * MinPerHour
SecPerDay = SecPerHour * HourPerDay

MilliPerSec = 1000
MilliPerMin = MilliPerSec * SecPerMin
MilliPerHour = MilliPerSec * SecPerHour
MilliPerDay = MilliPerSec * SecPerDay

MicroPerMilli = 1000
MicroPerSec = MicroPerMilli * MilliPerSec

NanoPerMicro = 1000
NanoPerMilli = NanoPerMicro * MicroPerMilli
NanoPerSec = NanoPerMilli * MilliPerSec
NanoPerMin = NanoPerSec * SecPerMin
NanoPerHour = NanoPerSec * SecPerHour
NanoPerDay = NanoPerSec * SecPerDay

TimestampNsT = int



def current_nanoseconds() -> NanosT:
    from cvttpy.tools.app import App
    return time.time_ns() if not App.instance().is_simulation_mode() else App.instance().simtime_ns()

def current_microseconds() -> int:
    return int(current_nanoseconds() / NanoPerMicro)


def current_milliseconds() -> int:
    return int(current_nanoseconds() / NanoPerMilli)


def current_seconds() -> float:
    return current_nanoseconds() / NanoPerSec


def current_tstamp() -> str:
    return format_nanos_utc(nanos=current_nanoseconds(), fmt="%Y%m%d_%H%M%S")


def current_dtstamp() -> str:
    return format_nanos_utc(nanos=current_nanoseconds(), fmt="%Y%m%d")

def format_time(ct: datetime.datetime, datefmt: Optional[str] = "%MY_TS_MICRO") -> str:
    datefmt = datefmt if datefmt is not None else "%MY_DTS_MILLI"
    if datefmt == "%MY_TS_MILLI":
        res = f"{ct.strftime('%H:%M:%S')}.{int(ct.microsecond / MicroPerMilli):.03d}"
    elif datefmt == "%MY_DTS_MILLI":
        res = f"{ct.strftime('%Y-%m-%d %H:%M:%S')}.{int(ct.microsecond / MicroPerMilli):.03d}"
    elif datefmt == "%MY_TS_MICRO":
        res = f"{ct.strftime('%H:%M:%S')}.{ct.microsecond:06d}"
    elif datefmt == "%MY_DTS_MICRO":
        res = f"{ct.strftime('%Y-%m-%d %H:%M:%S')}.{ct.microsecond:06d}"
    else:
        res = ct.strftime(datefmt)
    return res


def format_nanos(nanos: int, fmt: Optional[str] = "%MY_DTS_MICRO") -> str:
    tstmp: float = nanos / NanoPerSec
    ct: datetime.datetime = datetime.datetime.fromtimestamp(tstmp)
    return format_time(ct, fmt)


def format_nanos_utc(nanos: int, fmt: Optional[str] = "%MY_DTS_MICRO") -> str:
    if nanos == 0:
        return ""
    tstmp: float = nanos / NanoPerSec
    ct: datetime.datetime = datetime.datetime.utcfromtimestamp(tstmp)
    return format_time(ct, fmt)


def parse_to_nanos(timestr: str, format: str) -> int:
    return NanosT(
        datetime.datetime.strptime(timestr, format)
        .replace(tzinfo=datetime.timezone.utc)
        .timestamp()
        * NanoPerSec
    )

def format_current_utc_time(datefmt: Optional[str] = "%MY_TS_MICRO") -> str:
    return format_time(datetime.datetime.utcfromtimestamp(current_seconds()), datefmt)


def today_start_ns() -> TimestampNsT:
    cur = current_nanoseconds()
    return cur - (cur % NanoPerDay)

class Weekday(int, Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


def next_weekday_start_ns(wday: Weekday, tstr: str ) -> TimestampNsT:
    today = datetime.datetime.utcfromtimestamp(today_start_ns())
    delta = datetime.timedelta((7 + wday.value - today.weekday()) % 7)
    dtstr = (today + delta).strftime('%Y-%m-%d')
    res = parse_to_nanos(timestr=f"{dtstr} {tstr}", format="%Y-%m-%d %H:%M:%S")
    return res



if __name__ == "__main__":
    # tmstr = "2022-10-19T17:59:58+0000"
    # print(parse_to_nanos(tmstr[0:19], "%Y-%m-%dT%H:%M:%S"))

    print(next_weekday_start_ns(Weekday["Saturday"], '21:00:00'))
