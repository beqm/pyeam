from pyeam import core
from pyeam.core.config import Config


from System import Func, Type
from System.Drawing import Size, Icon
from System.Windows.Forms import Form, Application, FormBorderStyle


class WinForms(Form):
    def __init__(self, config: Config):
        super().__init__()
        self.uid = config.identifier

        self.Text = config.window.title
        self.Size = Size(config.window.width, config.window.height)
        self.MinimumSize = Size(config.window.min_width, config.window.min_height)

        if config.icon:
            self.Icon = Icon(config.icon)


        if not config.window.resizable:
            self.FormBorderStyle = FormBorderStyle.FixedSingle
        
        self.browser = core.Webview(self, config)

        self.FormClosed += self.on_exit

    def on_exit(self, *_):
        self.Invoke(Func[Type](self.Hide))
        self.browser.on_exit()

        Application.Exit()

def initialize(config: Config):
    form = WinForms(config)
    form.Show()

    app = Application
    app.Run()
    