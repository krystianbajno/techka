import importlib
import os
import importlib.util

def initialize(directories):
    return lambda dependencies: __load_plugins(directories, dependencies)
    
def __load_plugins(directories, dependencies):
    plugins = []
    for directory in directories:
        if os.path.exists(directory):
            for plugin_name in os.listdir(directory):
                plugin_path = os.path.join(directory, plugin_name, 'handler.py')
                if os.path.isfile(plugin_path):
                    plugin = __load_module(plugin_name, plugin_path, dependencies)
                    if plugin:
                        plugins.append(plugin)
    return plugins


def __load_module(module_name, path, dependencies):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        if hasattr(module, "Handler"):
            return module.Handler(dependencies)
        else:
            print(f"No Handler class found in {path}")
    except Exception as e:
        print(f"Failed to load handler from {module_name}: {e}")
    return None
