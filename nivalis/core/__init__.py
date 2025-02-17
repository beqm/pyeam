import os
import clr
import pythonnet
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).resolve().parents[1]
DLL_PATH = os.path.join(os.path.dirname(__file__), "dlls")

pythonnet.load("coreclr")
clr.AddReference("System")
clr.AddReference("System.Windows.Forms")

clr.AddReference(os.path.join(DLL_PATH, "Microsoft.Web.WebView2.Core.dll"))
clr.AddReference(os.path.join(DLL_PATH, "Microsoft.Web.WebView2.WinForms.dll"))


from nivalis.core.webview import Webview
from nivalis.core.winforms import WinForms