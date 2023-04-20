import PySimpleGUI as sg
import os
import pickle
from threading import Thread
import argparse
import enum
import ast

# ****************************************************************************
# *                                  Helpers                                 *
# ****************************************************************************

global_main_console = None

def get_selected(tree):
    tree = tree.widget
    curItem = tree.focus()
    return tree.item(curItem)

def log(message, text_color='white', lvl='info'):
    global global_main_console
    if global_main_console is not None:
        global_main_console.log(message, text_color=text_color, lvl=lvl)

def get_console():
    global global_main_console
    return global_main_console

def set_console(console):
    global global_main_console
    global_main_console = console

def string2dict(dict_string):
    return ast.literal_eval(dict_string)

def load_settings(window, filename='saved.settings', not_load=['-CONSOLE-']):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            saved_settings = pickle.load(f)
        for key in saved_settings:
            if key not in not_load:
                try:
                    if not isinstance(window[key], sg.Button):
                        window[key].update(value=saved_settings[key])
                except (TypeError, KeyError) as e:
                    print(e)
                    pass
        return saved_settings
    else:
        return None


def save_settings(values):
    with open('saved.settings', 'wb') as f:
        pickle.dump(values, f)

def str2type(string):
    # check if string type
    if not isinstance(string, str):
        return string
    teststring =  string.replace('-', '')
    if teststring.isnumeric():
        return int(string)
    elif teststring.replace('.', '', 1).isdigit():  # check if v is a floating-point number
        return float(string)
    elif teststring.lower() in ['true', 'yes', 'y']:
        return True
    elif teststring.lower() in ['false', 'no', 'n']:
        return False
    else:
        return string


#Hijacks tqdm to insert your own function
def hijack_tqdm(callback, auto=True):
    if auto:
        from tqdm.auto import tqdm
    else:
        from tqdm import tqdm
    orig_func = getattr(tqdm, "update")
    def wrapped_func(*args, **kwargs):
        pbar = args[0]
        v = orig_func(*args, **kwargs)
        callback({"value": pbar.n, "max": pbar.total})            
        return v
    setattr(tqdm, "update", wrapped_func)

def hijack_tqdm_progbar(prog_bar, auto):
    hijack_tqdm(lambda args: prog_bar.update(current_count=args['value'], max=args['max']), auto=auto)


def hijack_argparse(main_func, override_args):
    nw_args = argparse.Namespace()
    for k, v in override_args.items():
        if v != '':
            setattr(nw_args, k.replace('--', ''), str2type(v))

    def do_hj_argparse(*args, **kwargs):
        defaults = args[0].parse_known_args()[0]
        defaults_dict = vars(defaults)
        new_args_dict = vars(nw_args)

        enum_dict = {}

        for key in vars(defaults):
            arg_class = vars(defaults)[key]
            if isinstance(arg_class, enum.Enum):
                enum_dict[key] = arg_class.__class__

        for key in new_args_dict:
            if key in enum_dict:
                detected_enum = enum_dict[key]
                new_args_dict[key] = getattr(detected_enum, new_args_dict[key])

        hijacked_args_dict = {**defaults_dict, **new_args_dict}
        hijacked_args = argparse.Namespace(**hijacked_args_dict)
        return hijacked_args

    argparse.ArgumentParser.parse_args = do_hj_argparse
    main_func()

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
        global global_main_console
        global_main_console = self if main_console else global_main_console
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




