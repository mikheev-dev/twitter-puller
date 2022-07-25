from multiprocessing import Process

from lib.service.service import BaseService


class MPWrapper(Process):
    _service: BaseService

    def __init__(self, service: BaseService):
        super().__init__()
        self._service = service

    def run(self) -> None:
        self._service.run()
