import json
import logging
import threading
from pyeam.core.config import Config
from pyeam.core.invoker import Invoker
from concurrent.futures import ThreadPoolExecutor

from System.Diagnostics import Process
from System import Uri, Convert, Action
from System.Windows.Forms import DockStyle
from Microsoft.Web.WebView2.WinForms import WebView2


class Webview:
    logger = logging.getLogger("pyeam")

    def __init__(self, form, config: Config, workers: int):
        self.config = config
        self.webview = WebView2()
        self.thread_pool = ThreadPoolExecutor(max_workers=workers)
        self.logger.info(f"Running with {workers} workers")
        self.invoke_results = {}
        
        
        self.form = form
        form.Controls.Add(self.webview)
        
        self.webview.Dock = DockStyle.Fill
        self.webview.BringToFront()

        self.webview.CoreWebView2InitializationCompleted += self.on_webview_initialized
        self.webview.EnsureCoreWebView2Async(None)

        self.logger.info("Webview initialized")

    def on_webview_initialized(self, sender, args):
        """Configuration after webview is ready"""
        if not args.IsSuccess:
            self.logger.critical(f"Webview initialization failed: {str(args.InitializationException)}")
            return
        
        self.load_url(self.config.build.dev_url)
        
        settings = sender.CoreWebView2.Settings
        settings.AreDevToolsEnabled = self.config.dev_tools
        settings.AreDefaultContextMenusEnabled = self.config.context_menu

        self.logger.info(f"Webview DevTools: {self.config.dev_tools}")
        self.logger.info(f"Webview ContextMenu: {self.config.context_menu}")

        sender.CoreWebView2.WebMessageReceived += self.on_invoke
        self.logger.info("WebMessageReceived event handler registered")

    def on_invoke(self, sender, args):
        """Called when client requests a invoke"""
        try:
            message = args.WebMessageAsJson

            if message is None:
                self.logger.error("Invalid message")
                return
            
            payload = json.loads(message)

            request_name = payload.get("command")
            request_params = payload.get("params")
            request_id = payload.get("id")

            command = Invoker.commands.get(request_name)

            if not command or not command.allowed:
                self.logger.error(f"Command `{request_name}` not found.")
                return
            
            self.logger.info(f"Command called: `{request_name}`")
            
            self.thread_pool.submit(
                self.process_command,
                command, request_params, request_id
            )

        except Exception as err:
            self.logger.error(f"Failed to process invoke: {err}")

    def process_command(self, command, params, request_id):
        """Processa o comando em uma thread separada"""
        try:
            response = Invoker.process(command=command, params=params)
            self.invoke_results[request_id] = response
            

            self.webview.Invoke(
                Action(lambda: self.send_response(request_id))
            )
            
        except Exception as err:
            self.logger.error(f"Failed to run invoke: {err}")

    def send_response(self, request_id):
        """Envia a resposta do invoke_results para o cliente"""
        try:
            if request_id in self.invoke_results:
                result = self.invoke_results.pop(request_id)

                data = json.loads(result)

                response_data = {
                    "id": request_id,
                    "data": data["data"],
                    "error": data["error"]
                }

                self.webview.CoreWebView2.PostWebMessageAsString(json.dumps(response_data))
                self.logger.info(f"Response sent to {request_id}")
        except Exception as err:
            self.logger.error(f"Failed to sen response: {err}")

    def load_url(self, url):
        """Loads the url into the window"""
        self.webview.Source = Uri(url)
        self.logger.info("Client URL loaded into webview")


    def on_exit(self):
        """Terminates the webview process"""

        self.thread_pool.shutdown(wait=True)
        process_id = Convert.ToInt32(self.webview.CoreWebView2.BrowserProcessId)
        process = Process.GetProcessById(process_id)
        self.webview.Dispose()
        process.WaitForExit(3000)

        self.logger.info("Webview process terminated")

    def __del__(self):
        self.thread_pool.shutdown(wait=True)
