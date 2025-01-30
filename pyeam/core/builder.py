
import os
import psutil
import requests
import threading
import subprocess
from time import sleep
from pyeam.core.ipc import IPC
from pyeam.core import winforms
from typing import Callable, List
from pyeam.core.config import Config

from System.Windows.Forms import Application
from System.Threading import ApartmentState, Thread, ThreadStart

class Builder:
    config: Config
    ipc: IPC

    @staticmethod
    def default():
        conf = os.path.join(os.getcwd(), "pyeam.conf.json")
        Builder.config = Config.read(conf, "utf-8")

        return Builder()
    
    def run(self):
        try:
            ipc_thread: threading.Thread = IPC._run()
            ipc_thread.daemon = True
            ipc_thread.start()

            frontend_process: subprocess.Popen = Builder.wait_frontend()

            if not frontend_process:
                raise Exception("Failed to start frontend")

            Application.EnableVisualStyles()
            Application.SetCompatibleTextRenderingDefault(False)

            thread = Thread(ThreadStart(lambda: winforms.initialize(self.config)))
            thread.SetApartmentState(ApartmentState.STA)
            thread.Start()
            thread.Join()
        except Exception as err:
            print(err)
        finally:
            if frontend_process is not None:
                Builder.kill_processes(frontend_process.pid)



    def invokers(self, invokers: List[Callable]):
        for invoker in invokers:
            path = f"/api/invoke/{invoker.__name__}"
            if path not in IPC.routes:
                del IPC.routes[path]
                continue

            IPC._route(invoker.__name__, command=invoker, method="GET")

        return Builder()
    
    @staticmethod
    def kill_processes(parent_pid):
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()

    @staticmethod
    def wait_frontend() -> None:
        client_online = False
        print("Client running")
        while True:
            try:
                response = requests.head(Builder.config.build.dev_url)
                if response.status_code == 200:
                    if not client_online:
                        client_online = True
                    return
            except requests.RequestException as err:
                if not client_online:
                    process = subprocess.Popen(Builder.config.build.before_dev_command, shell=True, stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
                    client_online = True
                    return process
            sleep(1)