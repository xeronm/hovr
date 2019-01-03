import os
import importlib

def __load_and_merge_settings():
    module = importlib.import_module(os.environ.get('DJANGO_SETTINGS_MODULE_ORIG'))
    prefix = 'DJANGO_CONFIG_'
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        key_list = key[len(prefix):].split('_')
        key_target = module
        while key_list:
            subkey_list = [] 
            while not subkey_list or (key_list and key_list[0] == ''):
                 if key_list[0] == '':
                     key_list.pop(0)
                 subkey_list.append(key_list.pop(0))
            subkey = '_'.join(subkey_list)
            if isinstance(key_target, module.__class__) and hasattr(key_target, subkey):
                if key_list:
                    key_target = getattr(key_target, subkey)
                else:
                    setattr(key_target, subkey, value)
            elif isinstance(key_target, dict):
                if key_list:
                    key_target = key_target.get(subkey)
                else:
                    key_target[subkey] = value
            else:
                key_target = None
            if key_target is None:
                break
    G = globals()
    for k in dir(module):
        G[k] = getattr(module, k)

__load_and_merge_settings()
