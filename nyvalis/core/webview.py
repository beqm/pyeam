import json
from nyvalis.tools import log
from nyvalis.core.config import Config
from nyvalis.core.invoker import Invoker
from nyvalis.core import ROOT_PATH, LIB_NAME
from concurrent.futures import ThreadPoolExecutor

from System.Diagnostics import Process
from System import Uri, Convert, Action
from System.Windows.Forms import DockStyle
from Microsoft.Web.WebView2.WinForms import WebView2
from Microsoft.Web.WebView2.Core import (
    CoreWebView2WebResourceContext,
    CoreWebView2CustomSchemeRegistration,
    CoreWebView2EnvironmentOptions,
    CoreWebView2Environment
)
from System.IO import MemoryStream, SeekOrigin
from System.Collections.Generic import List



class Webview:
    logger = log.get(log.LIB_NAME)

    def __init__(self, form, config: Config, workers: int):
        self.config = config
        self.scheme = LIB_NAME
        self.webview = WebView2()
        self.thread_pool = ThreadPoolExecutor(max_workers=workers)
        self.logger.info(f"Running with {workers} workers")
        self.invoke_results = {}
        
        
        self.form = form
        form.Controls.Add(self.webview)
        
        self.webview.Dock = DockStyle.Fill
        self.webview.BringToFront()

        custom_scheme_registration = CoreWebView2CustomSchemeRegistration(self.scheme)
        custom_scheme_registration.TreatAsSecure = True
        custom_scheme_registration.HasAuthorityComponent = True

        custom_scheme_registrations = List[CoreWebView2CustomSchemeRegistration]()
        custom_scheme_registrations.Add(custom_scheme_registration)

        options = CoreWebView2EnvironmentOptions(
                additionalBrowserArguments=None,
                language=None,
                targetCompatibleBrowserVersion=None,
                allowSingleSignOnUsingOSPrimaryAccount=False,
                customSchemeRegistrations=custom_scheme_registrations
        )

        environment = CoreWebView2Environment.CreateAsync(None, None, options).GetAwaiter().GetResult()

        self.webview.CoreWebView2InitializationCompleted += self.on_webview_initialized
        self.webview.EnsureCoreWebView2Async(environment)

        self.logger.info("Webview initialized")

    def on_webview_initialized(self, sender, args):
        """Configuration after webview is ready"""
        if not args.IsSuccess:
            self.logger.critical(f"Webview initialization failed: {str(args.InitializationException)}")
            return
        
        self.webview.CoreWebView2.AddWebResourceRequestedFilter(f"{self.scheme}://*", CoreWebView2WebResourceContext.All)
        self.webview.CoreWebView2.WebResourceRequested += self.handle_custom_scheme_request
        self.logger.info("WebResourceRequested handler registered")

        if "__compiled__" in globals():
            url = f"{self.scheme}://app/"
            self.webview.CoreWebView2.Navigate(url)
        else:
            self.load_url(self.config.build.dev_url)
        
        settings = sender.CoreWebView2.Settings
        settings.AreDevToolsEnabled = self.config.dev_tools
        settings.AreDefaultContextMenusEnabled = self.config.context_menu

        self.logger.info(f"Webview DevTools: {self.config.dev_tools}")
        self.logger.info(f"Webview ContextMenu: {self.config.context_menu}")

        sender.CoreWebView2.WebMessageReceived += self.on_invoke
        self.logger.info("WebMessageReceived event handler registered")

    def handle_custom_scheme_request(self, sender, event_args):
        self.logger.debug(f"Request received: {event_args.Request.Uri}")

        if not event_args.Request.Uri.startswith(f"{self.scheme}://"):
            return None

        try:
            uri = event_args.Request.Uri
            parsed_uri = Uri(uri)
            
            raw_path = parsed_uri.AbsolutePath
            path = raw_path[1:] if raw_path.startswith('/') else raw_path
            
            base_dir = ROOT_PATH
            full_path = (base_dir / self.config.build.dist_dir / path).resolve()

            if not str(full_path).startswith(str(base_dir)):
                self.logger.warning(f"Permission denied: {full_path}")
                raise Exception(f"Permission denied: {full_path}")

            static_extensions = {'.js', '.css', '.png', '.jpg', '.svg', '.json', '.woff', '.woff2', '.ico'}

            if full_path.is_dir():
                full_path = full_path / "index.html"
            elif not full_path.exists():
                if full_path.suffix in static_extensions:
                    raise FileNotFoundError(f"File not found: {full_path}")
                full_path = base_dir / "index.html"
            if not full_path.is_file():
                raise FileNotFoundError(f"Not a file: {full_path}")

            mime_types = {
                '.html': 'text/html',
                '.js': 'application/javascript',
                '.mjs': 'application/javascript',
                '.css': 'text/css',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.svg': 'image/svg+xml',
                '.json': 'application/json',
                '.woff': 'font/woff',
                '.woff2': 'font/woff2',
                '.ico': 'image/x-icon'
            }

            ext = full_path.suffix.lower()
            content_type = mime_types.get(ext, 'application/octet-stream')

            self.logger.info(f"Serving: {full_path}: {content_type}")

            with open(full_path, "rb") as file:
                content = file.read()

            stream = MemoryStream(content)
            stream.Seek(0, SeekOrigin.Begin)
            
            response = self.webview.CoreWebView2.Environment.CreateWebResourceResponse(
                stream,
                200,
                "OK",
                f"Content-Type: {content_type}; charset=utf-8" if 'text/' in content_type else f"Content-Type: {content_type}"
            )
            event_args.Response = response

        except FileNotFoundError as err:
            self.logger.warning(f"File not found: {str(err)}")
            error_msg = "404 Not Found".encode("utf-8")
            error_stream = MemoryStream(error_msg)
            error_stream.Seek(0, SeekOrigin.Begin)
            
            response = self.webview.CoreWebView2.Environment.CreateWebResourceResponse(
                error_stream,
                404,
                "Not Found",
                "Content-Type: text/plain; charset=utf-8"
            )
            event_args.Response = response
            
        except Exception as err:
            self.logger.error(f"Error: {str(err)}", exc_info=True)
            error_msg = f"500 Server Error: {str(err)}".encode("utf-8")
            error_stream = MemoryStream(error_msg)
            error_stream.Seek(0, SeekOrigin.Begin)
            
            response = self.webview.CoreWebView2.Environment.CreateWebResourceResponse(
                error_stream,
                500,
                "Internal Server Error",
                "Content-Type: text/plain; charset=utf-8"
            )
            event_args.Response = response

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
        """Process the invoke in a different thread"""
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

    def load_html(self, content):
        with open(r"C:\Vault\Code\pc\testes\build\index.html", 'r', encoding='utf-8') as file:
            content = file.read()
        
        self.webview.CoreWebView2.NavigateToString(content)

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
