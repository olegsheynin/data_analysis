#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
import pprint
import signal
import sys
import threading
import time
import traceback
import warnings
from collections import namedtuple
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, Set

from aiohttp import web  # type:ignore
from umm.tools.base import NamedObject, Singleton
from umm.tools.logger import Log

import nest_asyncio
nest_asyncio.apply()

warnings.filterwarnings("error")


def dumpstacks(signal, frame=None):
    thrd_names_by_id: Dict = { th.ident:th.name for th in threading.enumerate()}

    code: List[str] = []
    code.append("=" * 80)
    for threadId, stack in sys._current_frames().items():
        code.append("# " + "-" * 78)
        code.append(f"# ---- Thread: {thrd_names_by_id.get(threadId,'')} ({threadId})")
        code.append("# " + "-" * 78)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append(f"File: {filename}, line {lineno}, in {name}")
            if line:
                code.append(f"\t{line.strip()}")
    code.append("=" * 80)

    msg = "\n".join(code)
    print(msg)
    Log.critical(msg)


class AdminService(NamedObject):
    server_: web.Application
    runner_: web.AppRunner
    port_: int
    URL_DESC = namedtuple("URL_DESC", ["method", "path", "help"])
    urls_: List[URL_DESC]
    run_task_: Optional[asyncio.Task]
    whitelist_: Set

    def __init__(self, port: int) -> None:
        self.server_ = web.Application()
        self.runner_ = web.AppRunner(self.server_)
        self.port_ = port
        self.urls_ = []
        self.run_task_ = None
        self.whitelist_ = set()

        App.instance().add_call(App.Stage.Run, self.run())
        App.instance().add_call(App.Stage.Stop, self.stop())

    def add_handler(self, path: str, coro, method: str = "GET", help="") -> None:
        if method.upper() not in ("GET", "POST"):
            raise Exception(f"method {method} is not implemented")

        if method.upper() == "GET":
            self.server_.add_routes([web.get(path, coro)])
        elif method.upper() == "POST":
            self.server_.add_routes([web.post(path, coro)])

        self.urls_.append(AdminService.URL_DESC(method.upper(), path, help))

    def all_urls(self) -> str:
        line = "-" * 80
        msgs = [
            line,
            f"ADMIN INTERFACES {'http://localhost:' + str(self.port_):>60}",
            line,
        ]
        for url_desc in sorted(self.urls_):
            msg = f"{url_desc.path:32}{url_desc.help:<50}"
            msgs.append(msg)
        msgs.append(line)
        msgs.append(App.instance().full_cmdline())
        return "\n".join(msgs)

    async def run(self) -> None:
        await self.runner_.setup()
        site = web.TCPSite(self.runner_, "0.0.0.0", self.port_)
        self.run_task_ = asyncio.current_task()
        Log.info(f"{self.name()} admin service is being started on port {self.port_}")
        await site.start()

    async def stop(self):
        await self.runner_.cleanup()
        if self.run_task_:
            self.run_task_.cancel()

    def validate_request(self, rqst: web.Request) -> bool:
        from umm.tools.umm_tools import UmmAppConfig
        if len(self.whitelist_) == 0:
            # allowed_clients should be array of IP addresses or string consisting of a comma-separated series of IP addresses
            local_clients = ["::1", "127.0.0.1"]
            allowed_clnts = UmmAppConfig.instance().get_value("installation/allowed_clients", [])
            if isinstance(allowed_clnts, str):
                allowed_clnts = [x.strip() for x in allowed_clnts.split(",")]
            self.whitelist_ = set([x for x in local_clients + allowed_clnts])
        return rqst.remote in self.whitelist_


class AppGlobals:
    run_key_: str = ""

    user_data_: Dict[str, Any] = {}


class App(NamedObject, metaclass=Singleton):
    instance: Callable[[], App]  # added by metaclass

    task_: Optional[asyncio.Future]
    admin_svc_: Optional[AdminService]
    enable_admin_svc_: bool
    admin_svc_port_: int
    perf_enabled_: bool
    loop_: Optional[asyncio.AbstractEventLoop]

    class Stage(IntEnum):
        Begin = 1
        Config = 2
        Start = 3
        Run = 4
        Stop = 5
        Exit = 6

        Shutdown = 101
        Undefined = -1

    funcs_: Dict[Stage, Any]
    signals_: List[signal.Signals]
    arg_parser_: argparse.ArgumentParser
    args_ns_: argparse.Namespace
    args_: Dict[str, Any]

    current_stage_: Stage
    multi_threaded_: bool

    def __init__(self) -> None:
        super().__init__()
        self.current_stage_ = App.Stage.Undefined

        self.signals_ = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]
        self.funcs_ = dict((stage, []) for stage in self.Stage)
        self.arg_parser_ = argparse.ArgumentParser()
        self._default_cmdline()

        self.task_ = None
        self.admin_svc_ = None
        self.loop_ = None
        self.multi_threaded_ = False
        self.perf_enabled_ = False

        self.add_cmdline_arg(
            "--admin_port",
            type=int,
            required=False,
            default=None,
            help="Admin svc port",
        )
        self.add_call(App.Stage.Begin, self.create_admin_svc())
        self.add_call(App.Stage.Start, self.register_default_admin())

    def _default_cmdline(self) -> None:
        self.add_cmdline_arg(
            "--log_level",
            required=False,
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"],
            default="INFO",
            help="Log Level",
        )
        self.add_cmdline_arg(
            "--log_file",
            type=str,
            required=False,
            default=None,
            help="Log File",
        )
        self.add_cmdline_arg(
            "--rotate_log",
            action="store_true",
            default=False,
            help="Rotate log at midnight",
        )
        self.add_cmdline_arg(
            "--compress_log",
            action="store_true",
            default=False,
            help="Log recorded compressed (gzip)",
        )
        self.add_cmdline_arg(
            "--log_stdout",
            action="store_true",
            default=False,
            help="Print to stdout (along with given log file)",
        )
        self.add_cmdline_arg(
            "--multi_threaded",
            action="store_true",
            default=False,
            required=False,
            help="Run some functions (e.g. md) in separate threads",
        )
        self.add_cmdline_arg(
            "--perf_enabled",
            action="store_true",
            default=False,
            required=False,
            help="Enable Performance Measuring",
        )

    def add_cmdline_arg(self, *args, **kwargs) -> None:
        self.arg_parser_.add_argument(*args, **kwargs)

    def _parse_cmdline(self) -> None:
        self.args_ns_ = self.arg_parser_.parse_args()
        self.args_ = vars(self.args_ns_)
        Log(
            log_level=self.args_["log_level"],
            log_file=self.args_["log_file"],
            rotate_log=self.args_["rotate_log"],
            compress_log=self.args_["compress_log"],
            log_stdout=self.args_["log_stdout"],
        )
        Log.info(f"Version: {os.path.realpath(sys.argv[0])}")
        Log.info(f"CommandLine={pprint.pformat(self.args_)}")
        self.multi_threaded_ = self.args_["multi_threaded"]
        self.perf_enabled_ = self.args_["perf_enabled"]
        Log.info(f"Performance Measuring is {'ON' if self.perf_enabled_ else 'OFF'}")

    def perf_enabled(self) -> bool:
        return self.perf_enabled_


    def full_cmdline(self) -> str:
        res = f"{os.path.realpath(sys.argv[0]) }"
        res += " ".join([f"--{arg}={val}" for arg, val in self.args_.items()])
        return res

    def add_call(self, stage: App.Stage, func: Any) -> None:
        # TBD compare stage with current stage, if later, run immediately.
        self.funcs_[stage].append(func)

    def _prepare_run(self) -> None:
        self._parse_cmdline()

    async def create_admin_svc(self) -> None:
        admin_port = self.args_.get("admin_port", None)
        if admin_port is None:
            self.enable_admin_svc_ = False
            Log.debug("--admin_port is not specified. running with no admin service")
        else:
            self.enable_admin_svc_ = True
            self.admin_svc_port_ = admin_port
            self.admin_svc_ = AdminService(self.admin_svc_port_)

    async def register_default_admin(self) -> None:
        if self.admin_svc_:
            self.admin_svc_.add_handler(
                path="/shutdown", coro=self.admin_shutdown, help="terminate application"
            )
            self.admin_svc_.add_handler(path="/ping", coro=self.admin_ping, help="ping")
            self.admin_svc_.add_handler(
                path="/",
                coro=self.admin_interfaces_list,
                help="list of available admin interfaces",
            )
            self.admin_svc_.add_handler(
                path="/log_level",
                coro=self.admin_log_level,
                help="log_level?[debug|info|warning|error|fatal]",
            )
            self.admin_svc_.add_handler(
                path="/version", coro=self.admin_version, help="application version"
            )
            self.admin_svc_.add_handler(
                path="/cmdline", coro=self.cmdln_args, help="full command line"
            )

    async def admin_version(self, rqst: web.Request) -> web.Response:
        if self.admin_svc_ and self.admin_svc_.validate_request(rqst):
            return web.Response(text=f"{os.path.realpath(sys.argv[0])}\n")
        return web.Response()

    async def cmdln_args(self, rqst: web.Request) -> web.Response:
        if self.admin_svc_ and self.admin_svc_.validate_request(rqst):
            return web.Response(text=f"{self.full_cmdline()}\n")
        return web.Response()

    async def admin_log_level(self, rqst: web.Request) -> web.Response:
        msg = ""
        if self.admin_svc_ and self.admin_svc_.validate_request(rqst):
            log_level: str = rqst.query_string.upper()
            if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "FATAL"):
                return web.Response(
                    status=404,
                    text=f"http://localhost:{self.admin_svc_.port_}/log_level?[debug|info|warning|error|fatal]\n",
                )

            Log.set_level(log_level)
            msg = f"Log level is changed to {log_level}\n"
            Log.warning(msg)
            return web.Response(text=msg)
        return web.Response()

    async def admin_shutdown(self, rqst) -> web.Response:
        if self.admin_svc_ and self.admin_svc_.validate_request(rqst):
            Log.warning(f"{self.name()} received admin shutdown request")
            self.shutdown()
            # await asyncio.gather(*self.funcs_[self.Stage.Shutdown])
        return web.Response()

    async def admin_ping(self, rqst) -> web.Response:
        return web.Response(text="pong\n")

    async def admin_interfaces_list(self, rqst) -> web.Response:
        if self.admin_svc_:
            return web.Response(text=f"{self.admin_svc_.all_urls()}\n")
        return web.Response()

    def validate_admin_request(self, rqst: web.Request) -> bool:
        # trivial yet, only localhost
        return rqst.remote == "127.0.0.1"

    def async_sig_handler(self, sig: signal.Signals) -> None:
        Log.info(f"received signal {sig.name}")
        self.shutdown()

    def admin_svc(self) -> Optional[AdminService]:
        return self.admin_svc_

    def run(self) -> None:
        try:
            self._run()
        except (KeyboardInterrupt, SystemExit):
            self.exit()
        except Exception as expt:
            print(f"{expt}\n{traceback.format_exc()}", file=sys.stderr)
            self.stop()

        self.exit()

    def _run(self) -> None:
        self._prepare_run()

        self.loop_ = asyncio.get_event_loop()
        for sig in self.signals_:
            self.loop_.add_signal_handler(sig, self.async_sig_handler, sig)

        signal.signal(signal.SIGUSR1, dumpstacks)

        for stage in [
            App.Stage(stg.value)
            for stg in App.Stage
            if stg.value <= App.Stage.Exit.value
        ]:
            try:
                self.run_stage(stage)
            except:
                break

    def run_stage(self, stage: App.Stage) -> None:
        self.current_stage_ = stage
        if stage not in self.funcs_ or len(self.funcs_[stage]) == 0:
            return
        self.task_ = asyncio.gather(*self.funcs_[self.current_stage_])
        if self.task_:
            if not self.loop_:
                self.loop_ = asyncio.get_running_loop()
            try:
                self.loop_.run_until_complete(self.task_)
            except:
                Log.error(traceback.format_exc())
                pass

    def shutdown(self) -> None:
        if self.task_:
            self.task_.cancel()
            self.task_ = None
        self.stop()

    def stop(self) -> None:
        Log.flush()
        if not self.loop_:
            self.loop_ = asyncio.get_running_loop()

        for stage in (App.Stage.Shutdown, App.Stage.Stop, App.Stage.Exit):
            Log.info(f"{self.name()}: Stage {stage.name} begin")
            self.run_stage(stage)
            Log.info(f"{self.name()}: Stage {stage.name} end")
        self.exit()

    def exit(self, exit_code: int = 0, sig=signal.SIGKILL) -> None:
        Log.flush()
        # if threading.current_thread() is threading.main_thread():
        #     sys.exit(exit_code)
        # else:
        if True:
            # sys.exit works only from the main thread
            os.kill(os.getpid(), sig)

    def is_simulation_mode(self) -> bool:
        return False


class SimApp(App):
    simtime_ns_: TimestampNsT

    def __init__(self) -> None:
        super().__init__()
        self.simtime_ns_ = 0

    def is_simulation_mode(self) -> bool:
        return True

    def set_simtime_ns(self, simtime: TimestampNsT) -> None:
        self.simtime_ns_ = simtime

    def simtime_ns(self) -> TimestampNsT:
        return self.simtime_ns_

if __name__ == "__main__":

    def test1() -> None:
        async def hello(request):
            print("hello was called")
            return web.Response()

        async def sleep():
            await asyncio.sleep(30)

        srv = AdminService(5555)
        srv.add_handler("/", hello)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[srv.run(), sleep()]))
    test1()
