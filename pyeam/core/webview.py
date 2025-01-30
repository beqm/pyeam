from pyeam.core.config import Config

from System import Uri
from System import Convert, Uri
from System.Diagnostics import Process
from System.Windows.Forms import DockStyle
from System.Threading.Tasks import TaskScheduler
from Microsoft.Web.WebView2.WinForms import WebView2


class Webview:
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

    def on_webview_initialized(self, sender, args):
        if not args.IsSuccess:
            print(f"Failed with: {str(args.InitializationException)}")
            return
        
        self.load_url(self.config.build.dev_url)
        
        settings = sender.CoreWebView2.Settings
        settings.AreDevToolsEnabled = self.config.dev_tools
        settings.AreDefaultContextMenusEnabled = self.config.context_menu



    def load_url(self, url):
        self.webview.Source = Uri(url)

    def on_exit(self):
        process_id = Convert.ToInt32(self.webview.CoreWebView2.BrowserProcessId)
        process = Process.GetProcessById(process_id)
        self.webview.Dispose()
        process.WaitForExit(3000)