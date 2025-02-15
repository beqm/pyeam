from System.Reflection import BindingFlags, Assembly
from System.Windows.Forms import OpenFileDialog, DialogResult, MessageBox, MessageBoxButtons
from System import UInt32, Object, Array


from typing import List
from dataclasses import dataclass

@dataclass
class FileFilter:
    text: str
    extension: List[str]

    def __str__(self):
        ext_str = ";".join(f"*{ext}" for ext in self.extension)
        return f"{self.text} ({ext_str})|{ext_str}"


class Dialog:
    __FOLDERS_FILTER = 'Folders'
    __FLAGS = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic
    __winforms_assembly = Assembly.LoadWithPartialName('System.Windows.Forms')

    __i_file_dialog_type = __winforms_assembly.GetType('System.Windows.Forms.FileDialogNative+IFileDialog')
    __open_file_dialog_type = __winforms_assembly.GetType('System.Windows.Forms.OpenFileDialog')
    __file_dialog_type = __winforms_assembly.GetType('System.Windows.Forms.FileDialog')
    __create_vista_dialog = __open_file_dialog_type.GetMethod('CreateVistaDialog', __FLAGS)
    __on_before_vista_dialog = __open_file_dialog_type.GetMethod('OnBeforeVistaDialog', __FLAGS)
    __get_options = __file_dialog_type.GetMethod('GetOptions', __FLAGS)
    __set_options = __i_file_dialog_type.GetMethod('SetOptions', __FLAGS)
    __fos_pick_folders = __winforms_assembly.GetType('System.Windows.Forms.FileDialogNative+FOS')\
        .GetField('FOS_PICKFOLDERS').GetValue(None)

    __vista_dialog_events_constructor = __winforms_assembly.GetType(
        'System.Windows.Forms.FileDialog+VistaDialogEvents'
    ).GetConstructor(__FLAGS, None, [__file_dialog_type], [])
    __advise_method = __i_file_dialog_type.GetMethod('Advise')
    __show_method = __i_file_dialog_type.GetMethod('Show')

    @staticmethod
    def open(title: str, directory: bool = False, multiple: bool = False, path=None, filters: List[FileFilter]=[]):
        dialog = OpenFileDialog()
        dialog.Title = title
        dialog.Multiselect = multiple
        dialog.InitialDirectory = path

        if directory:
            dialog.Filter = Dialog.__FOLDERS_FILTER
            dialog.CheckFileExists = False
            dialog.DereferenceLinks = True
            dialog.AddExtension = False
            dialog.RestoreDirectory = True

            i_file_dialog = Dialog.__create_vista_dialog.Invoke(dialog, [])
            Dialog.__on_before_vista_dialog.Invoke(dialog, [i_file_dialog])
            options = Dialog.__get_options.Invoke(dialog, [])
            options = options.op_BitwiseOr(Dialog.__fos_pick_folders)
            Dialog.__set_options.Invoke(i_file_dialog, [options])

            advise_params = Array.CreateInstance(Object, 2)
            advise_params[0] = Dialog.__vista_dialog_events_constructor.Invoke([dialog])
            advise_params[1] = UInt32(0)
            Dialog.__advise_method.Invoke(i_file_dialog, advise_params)

            result = Dialog.__show_method.Invoke(i_file_dialog, [None])
            return list(dialog.FileNames) if result == 0 else None

        filter_strings = [str(f) for f in filters]
        filter_strings.append("All Files (*.*)|*.*")
        filter = "|".join(filter_strings)

        dialog.Filter = filter if filters else "All Files|*.*" 
        dialog.RestoreDirectory = True
        result = dialog.ShowDialog()
        return list(dialog.FileNames) if result == DialogResult.OK else None

    @staticmethod
    def confirmation(title: str, message: str) -> bool:
        result = MessageBox.Show(message, title, MessageBoxButtons.OKCancel)
        return result == DialogResult.OK
    
open = Dialog.open
confirmation = Dialog.confirmation
