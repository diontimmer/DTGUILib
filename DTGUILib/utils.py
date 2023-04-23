import PySimpleGUI as sg
import os
import pickle
import argparse
import enum
import ast
import DTGUILib.const as dtc
import DTGUILib.current_gui as dtcurrent

# ****************************************************************************
# *                                  Utils                                   *
# ****************************************************************************

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return False
    else:
        return True

def get_selected(tree):
    tree = tree.widget
    curItem = tree.focus()
    return tree.item(curItem)

def log(message, text_color='white', lvl='info'):
    if dtcurrent.current_console is not None:
        dtcurrent.current_console.log(message, text_color=text_color, lvl=lvl)

def get_console():
    return dtcurrent.current_console

def set_console(console):
    dtcurrent.current_console = console

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




