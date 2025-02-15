
import logging
from nivalis.tools import log

logger = log.get(log.LIB_LOGGER)
logger.setLevel(logging.NOTSET)
handler = logging.StreamHandler()
handler.setFormatter(log.handlers.CustomFormatter(log.DEFAULT_FMT, log.DEFAULT_DATEFMT, colored=True, iso=True))
logger.addHandler(handler)
logger.propagate = False


import os
import psutil
import requests
import subprocess
from time import sleep
from nivalis.tools import stdout
from nivalis.core import winforms
from typing import Callable, List
from nivalis.core.config import Config
from nivalis.core.invoker import Invoker

from System.Windows.Forms import Application
from System.Threading import ApartmentState, Thread, ThreadStart

class NivalisClientError(Exception):
    """Exception for client"""
    pass


class Builder:
    config: Config
    logger = log.get(log.LIB_LOGGER)
    _workers = 2

    @classmethod
    def default(cls):
        from nivalis.core.config.exceptions import NivalisConfigError
        try:
            stdout.info("Starting application")
            cls.logger.info(f"Starting builder")
            conf = os.path.join(os.getcwd(), "nivalis.conf.json")

            cls.logger.info(f"Loading nivalis.conf.json")
            Builder.config = Config.read(conf, "utf-8")
            return Builder()
        except NivalisConfigError as err:
            stdout.error(f"{err}", exit=True)
    
    @classmethod
    def run(cls) -> None:
        client_process = None
        
        try:
            client_process = Builder.wait_client()

            if not client_process:
                stdout.error("Failed to start client")
                raise NivalisClientError("Failed to start client")

            Application.EnableVisualStyles()
            Application.SetCompatibleTextRenderingDefault(False)

            thread = Thread(ThreadStart(lambda: winforms.initialize(cls.config, cls._workers)))
            thread.SetApartmentState(ApartmentState.STA)
            thread.Start()
            thread.Join()
        except Exception as err:
            stdout.error(f"Failed running builder: {err}")
            cls.logger.critical(f"Failed running builder: {err}")
        finally:
            if client_process is not None:
                Builder.kill_processes(client_process.pid)

    @classmethod
    def invokers(cls, invokers: List[Callable]):
        for invoker in invokers:
            name = invoker.__name__
            if Invoker.commands.get(name):
                Invoker.commands[name].allowed = True
                cls.logger.info(f"Registering command: `{name}` ")
                
        return Builder()
    
    @classmethod
    def workers(self, amount: int) -> "Builder":
        self.workers = amount
        return Builder

    
    @classmethod
    def kill_processes(cls, parent_pid):
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        cls.logger.info(f"Client terminated")
        log.Env.__del__(log.Env)
        cls.logger.info(f"QueueListener stopped")


    @classmethod
    def wait_client(cls) -> None:
        client_online = False
        while True:
            try:
                cls.logger.info(f"Checking {Builder.config.build.dev_url} status")
                response = requests.head(Builder.config.build.dev_url)
                if response.status_code == 200:
                    if not client_online:
                        client_online = True
                    return
            except requests.RequestException:
                cls.logger.info("Status: offline")
                if not client_online:
                    cls.logger.info("Starting frontend process")
                    process = subprocess.Popen(Builder.config.build.before_dev_command, shell=True, stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
                    cls.logger.info("Success")
                    client_online = True
                    cls.logger.info("Returning process")
                    return process
            sleep(0.25)