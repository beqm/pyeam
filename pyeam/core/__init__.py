import os
import clr
import pythonnet

DLL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dlls")

pythonnet.load("coreclr")
clr.AddReference("System")
clr.AddReference("System.Windows.Forms")

clr.AddReference(os.path.join(DLL_PATH, "Microsoft.Web.WebView2.Core.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Microsoft.Web.WebView2.WinForms.dll"))


from pyeam.core.webview import Webview
from pyeam.core.winforms import WinForms