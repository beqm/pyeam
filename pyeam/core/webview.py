import json
import logging
from pyeam.core.config import Config
from pyeam.core.invoker import Invoker

from System import Uri
from System import Convert, Uri
from System.Diagnostics import Process
from System.Windows.Forms import DockStyle
from System.Threading.Tasks import TaskScheduler
from Microsoft.Web.WebView2.WinForms import WebView2


class Webview:
    logger = logging.getLogger("pyeam")

    def __init__(self, form, config: Config):
        self.config = config
        self.webview = WebView2()

        self.form = form
        form.Controls.Add(self.webview)
        
        self.webview.Dock = DockStyle.Fill
        self.webview.BringToFront()

        self.webview.CoreWebView2InitializationCompleted += self.on_webview_initialized
        self.syncContextTaskScheduler = TaskScheduler.FromCurrentSynchronizationContext()
        
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

            name = payload.get("command")
            params = payload.get("params")

            command = Invoker.commands.get(name)

            if not command or not command.allowed:
                self.logger.error(f"Command `{name}` not found.")
                return
            
            self.logger.info(f"Command called: `{name}`")
            response = Invoker.process(command=command, params=params)
            self.send_response(response)

        except Exception as err:
            self.logger.error(f"Failed to process invoke: {err}")


    def send_response(self, message):
        """Returns a reponse to the client"""
        try:
            self.webview.CoreWebView2.PostWebMessageAsString(str(message))
            self.logger.info(f"Response sent to client")
        except Exception as err:
            self.logger.error(f"Failed to send reponse: {err}")

    def load_url(self, url):
        """Loads the url into the window"""
        self.webview.Source = Uri(url)
        self.logger.info("Client URL loaded into webview")

    def on_exit(self):
        """Terminates the webview process"""
        process_id = Convert.ToInt32(self.webview.CoreWebView2.BrowserProcessId)
        process = Process.GetProcessById(process_id)
        self.webview.Dispose()
        process.WaitForExit(3000)

        self.logger.info("Webview process terminated")
