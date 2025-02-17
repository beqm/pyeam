from nivalis import core
from nivalis.tools import log
from nivalis.core.config import Config


from System import Func, Type
from System.Drawing import Size, Icon
from System.Windows.Forms import Form, Application, FormBorderStyle


class WinForms(Form):
    logger = log.get(log.LIB_LOGGER)

    def __init__(self, config: Config, workers: int):
        super().__init__()
        self.uid = config.identifier

        self.Text = config.window.title
        self.Size = Size(config.window.width, config.window.height)
        self.MinimumSize = Size(config.window.min_width, config.window.min_height)

        self.logger.info(f"WinForms Window UUID: {config.identifier}")
        self.logger.info(f"WinForms Window Text: {config.window.title}")
        self.logger.info(f"WinForms Window Size: {config.window.width}x{config.window.height}")
        self.logger.info(f"WinForms Window MinimumSize: {config.window.min_width}x{config.window.min_height}")

        self.logger.info("WinForms successfully configurated")

        if config.icon:
            self.Icon = Icon(config.icon)
            self.logger.info(f"WinForms Icon: {config.icon}")


        if not config.window.resizable:
            self.FormBorderStyle = FormBorderStyle.FixedSingle
        self.logger.info(f"WinForms Window Resizable: {config.window.resizable}")
        
        self.browser = core.Webview(self, config, workers)
        self.FormClosed += self.on_exit

    def on_exit(self, *_):
        self.logger.info("WinForms Exit requested")
        self.Invoke(Func[Type](self.Hide))
        self.browser.on_exit()
        Application.Exit()

        self.logger.info("WinForms process terminated")

def initialize(config: Config, workers: int):
    """Starts the application"""
    logger = log.get(log.LIB_LOGGER)

    form = WinForms(config, workers)
    form.Show()

    app = Application
    logger.info("Application started")
    app.Run()
