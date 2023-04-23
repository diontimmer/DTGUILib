import PySimpleGUI as sg
from threading import Thread
import DTGUILib.current_gui as dtcurrent

# ****************************************************************************
# *                                 Elements                                 *
# ****************************************************************************

# Settings

def Number_Setting(text, default, key, expand_x=True, expand_y=False, size=(None, None)):
    return [sg.Text(text), sg.InputText(default_text=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None))]

def Bool_Setting(text, key, default=True, expand_x=True, expand_y=False, size=(None, None)):
    return [sg.Checkbox(text, default=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None))]

def String_Setting(text, default, key, expand_x=True, expand_y=False, size=(None, None)):
    return [sg.Text(text), sg.InputText(default_text=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None))]

def File_Setting(text, default, key, expand_x=True, expand_y=False, file_types=None, size=(None, None)):
    return [sg.Text(text), sg.InputText(default_text=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None)), sg.FileBrowse(file_types=file_types)]

def Folder_Setting(text, default, key, expand_x=True, expand_y=False, size=(None, None)):
    return [sg.Text(text), sg.InputText(default_text=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None)), sg.FolderBrowse()]

def Enum_Setting(text, enum, default, key, expand_x=True, expand_y=False, size=(None, None)):
    return [sg.Text(text), sg.Combo(enum._member_names_, default_value=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None))]

def List_Setting(text, list, default, key, expand_x=True, expand_y=False, size=(None, None)):
    return [sg.Text(text), sg.Combo(list, default_value=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None))]

def TextBox_Setting(text, default, key, expand_x=True, expand_y=False, size=(None, None)):
    return [sg.Text(text), sg.Multiline(default_text=default, key=key, expand_x=expand_x, expand_y=expand_y, size=(None, None))]

# Shows a splash screen

class SplashScreen():
    def __init__(self, image_path=None):
        self.image_path = image_path
        self.splash = None

    def show(self):
        if self.image_path is not None:
            image = [sg.Image(filename=self.image_path)]
        else:
            image = [sg.Text('Loading...', font='Helvetica 40')]
        splash = sg.Window('Window Title', [image], transparent_color=sg.theme_background_color(), no_titlebar=True, keep_on_top=True)
        splash.read(timeout=0)
        self.splash = splash

    def close(self):
        if self.splash:
            self.splash.close()


# Console

class ConsoleClass(sg.Multiline):
    def __init__(self, main_console=True, route_err=True, size=(10,15), expand_x=True, *args, **kwargs):
        dtcurrent.current_console = self if main_console else dtcurrent.current_console
        super().__init__(reroute_stderr=route_err, size=size, expand_x=expand_x, autoscroll=True, write_only=True, disabled=True, auto_refresh=True, reroute_cprint=True, key='-CONSOLE-', *args, **kwargs)

    def log(self, *args, **kwargs):
        kwargs['lvl'] = kwargs['lvl'].lower()
        args = list(args)
        if kwargs['lvl'] == 'raw':
            pass
        elif kwargs['lvl'] == 'info':
            args[0] = f"[INFO] {args[0]}"
        elif kwargs['lvl'] == 'warning':
            args[0] = f"[WARNING] {args[0]}"
            kwargs['text_color'] = 'yellow'
        elif kwargs['lvl'] == 'loading':
            args[0] = f"[LOADING] {args[0]}"
            kwargs['text_color'] = 'gold'
        elif kwargs['lvl'] == 'nonurgent':
            args[0] = f"[WARNING] {args[0]}"
            kwargs['text_color'] = 'orange'
        elif kwargs['lvl'] == 'error':
            args[0] = f"[ERROR] {args[0]}"
            kwargs['text_color'] = 'red'
        elif kwargs['lvl'] == 'success':
            args[0] = f"[SUCCESS] {args[0]}"
            kwargs['text_color'] = 'green'
        elif kwargs['lvl'] == 'debug':
            args[0] = f"[DEBUG] {args[0]}"
            kwargs['text_color'] = 'lightblue'
        del kwargs['lvl']
        args = tuple(args)
        sg.cprint(*args, **kwargs)

class ConsoleInput(sg.Multiline):
    def __init__(self, console, command_dict, *args, **kwargs):
        self.console = console
        self.command_dict = command_dict
        super().__init__(no_scrollbar=True, key='-INPUT-', *args, **kwargs)
    def submit_input(self, window):
        cinput = self.get()
        #python eval
        if cinput.startswith("!python "):
            cinput = cinput.replace("!python ", "")
            eval(cinput)
        else:
            cmd = cinput.split(' ')[0]
            args = cinput.split(' ')[1:]
            if cmd in self.command_dict:
                Thread(target=self.command_dict[cmd], args=(window, self.console, args)).start()
            else:
                self.console.log("Command not found", text_color='red')
        self.update(value='')

# Tree Override

class TreeData(sg.TreeData):

    def __init__(self):
        super().__init__()

    def move(self, key1, key2):
        if key1 == '' and not self.is_legal_move(key1, key2):
            return False
        node = self.tree_dict[key1]
        parent1_node = self.tree_dict[node.parent]
        parent1_node.children.remove(node)
        parent2_node = self.tree_dict[key2]
        parent2_node.children.append(node)
        node.parent = parent2_node.key
        return True

    def delete(self, node):
        if not node:
            # If the node is None, return False
            return False
        parent_key = node.parent
        parent_node = self.tree_dict[parent_key]
        if not parent_node.children or node not in parent_node.children:
            # If the parent node doesn't have any children or the node is not in the parent's children list, return False
            return False
        parent_node.children.remove(node)
        node_list = [node, ]
        while node_list != []:
            temp = []
            for item in node_list:
                temp += item.children
                del item
            node_list = temp
        return True

    
    def is_legal_move(self, key1, key2):
    
        node_list = [self.tree_dict[key1], ]
        node2 = self.tree_dict[key2]
    
        while node_list != []:
            if node2 in node_list:
                return False
            temp = []
            for node in node_list:
                temp += node.children
            node_list = temp
    
        return True

# themes

sg.theme_add_new(
    'DTGUI_PINK', 
    {
        'BACKGROUND': '#242834', 
        'TEXT': '#f9dff9', 
        'INPUT': '#de1b73', 
        'TEXT_INPUT': '#FFFFFF', 
        'SCROLL': '#a9afbb', 
        'BUTTON': ('#FFFFFF', '#de1b73'), 
        'PROGRESS': ('#31ff0d', '#5b9760'), 
        'BORDER': 1, 
        'SLIDER_DEPTH': 0, 
        'PROGRESS_DEPTH': 0, 
    }
)

sg.theme_add_new(
    'DTGUI_BLUE', 
    {
        'BACKGROUND': '#242834', 
        'TEXT': '#def3fa', 
        'INPUT': '#1a7cdf', 
        'TEXT_INPUT': '#FFFFFF', 
        'SCROLL': '#a9afbb', 
        'BUTTON': ('#FFFFFF', '#1b69de'), 
        'PROGRESS': ('#31ff0d', '#5b9760'), 
        'BORDER': 1, 
        'SLIDER_DEPTH': 0, 
        'PROGRESS_DEPTH': 0, 
    }
)

sg.theme_add_new(
    'DTGUI_GREEN', 
    {
        'BACKGROUND': '#242834', 
        'TEXT': '#defaed', 
        'INPUT': '#11bb73', 
        'TEXT_INPUT': '#FFFFFF', 
        'SCROLL': '#a9afbb', 
        'BUTTON': ('#FFFFFF', '#1aa268'), 
        'PROGRESS': ('#31ff0d', '#5b9760'), 
        'BORDER': 1, 
        'SLIDER_DEPTH': 0, 
        'PROGRESS_DEPTH': 0, 
    }
)




