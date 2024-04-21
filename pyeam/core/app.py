import os
import time
import psutil
import webview
import requests
import threading
import subprocess
from pyeam.api.client import ClientServer
from pyeam.core.config import ConfigHandler
from pyeam.core.models import Config, Result

class Builder:

    _config: Config = ConfigHandler._read()

    @staticmethod
    def _wait_for_frontend() -> Result:
        server_running = False  # Flag to track server status
        print(f"Client running on {Builder._config.build.dev_url}")
        while True:
            try:
                response = requests.head(Builder._config.build.dev_url)
                if response.status_code == 200:
                    if not server_running:
                        server_running = True
                    return Result(success=True)
            except requests.RequestException:
                if not server_running:
                    frontend_process = subprocess.Popen(Builder._config.build.dev_command, shell=True)
                    server_running = True
                    return Result(success=True, data=frontend_process)
            time.sleep(1)

            
    @staticmethod
    def _kill_child_processes(parent_pid):
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()


    @staticmethod
    def run() -> None:
        try:
            os.system('cls')
            client_thread: threading.Thread = ClientServer._run()
            client_thread.daemon = True
            client_thread.start()

            frontend_result: Result = Builder._wait_for_frontend()
            frontend_process: subprocess.Popen = frontend_result.data


            if frontend_result.success:
                main_window = webview.create_window(url=Builder._config.build.dev_url, 
                                        title=Builder._config.window.title,
                                        width=Builder._config.window.width, 
                                        height=Builder._config.window.height, 
                                        resizable=Builder._config.window.resizable)
                webview.start(debug=True)
        except KeyboardInterrupt:
            print(f"Closing application..")
        finally:
            if frontend_process is not None:
                Builder._kill_child_processes(frontend_process.pid)
            main_window.destroy()



