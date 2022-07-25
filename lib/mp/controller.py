from logging import Logger
from typing import Dict

import copy
import time

from lib.mp.wrapper import MPWrapper
from lib.service.service import BaseService

CONTROL_TIME = 60


class MPController(BaseService):
    _logger: Logger
    _processes: Dict[str, MPWrapper]
    _controlled_processes: Dict[str, MPWrapper]

    def _start_process(self, p_name: str) -> MPWrapper:
        self._controlled_processes[p_name] = copy.copy(self._processes[p_name])
        self._controlled_processes[p_name].start()
        return self._controlled_processes[p_name]

    def main(self):
        for p_name, p in self._controlled_processes.items():
            self._logger.info(f"Status process {p._service._service_name} pid={p.pid}: is_alive={p.is_alive()}")
            if not p.is_alive():
                self._logger.info(f"{self._service_name}::Process {p.pid} is down, restart it!")
                self._start_process(p_name=p_name)
        time.sleep(CONTROL_TIME)

    def setup(self):
        self._controlled_processes = {}
        self._logger.debug(f"{self._service_name}::Start control processes!")
        for p_name in self._processes.keys():
            p = self._start_process(p_name=p_name)
            self._logger.info(f"Service {p._service._service_name}: Pid {p.pid}")
