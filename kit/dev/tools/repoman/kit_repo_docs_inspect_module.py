
import importlib
import inspect
import json
import os
import sys
import traceback
from pathlib import Path


def inspect_modules(modules):

    output = {}

    for m in modules:
        print(f"inspecting contents of module {m}")

        imported = False
        try:
            module = importlib.import_module(m)
            imported = True
        except Exception as e:
            print(f"failed importing module {m}. Traceback:")
            traceback.print_tb(e.__traceback__)
            print(e)

        if not imported:
            continue

        module_all = module.__all__ if "__all__" in dir(module) else None
        if module_all == []:
            continue
        if not module_all:
            module_all == []

        m_id = id(sys.modules[m])
        doc = inspect.getdoc(sys.modules[m])

        classes_check = inspect.getmembers(sys.modules[m], predicate=inspect.isclass)
        functions_check = inspect.getmembers(sys.modules[m], predicate=inspect.isfunction)
        builtins_check = inspect.getmembers(sys.modules[m], predicate=inspect.isbuiltin)
        submodules_check = inspect.getmembers(sys.modules[m], predicate=inspect.ismodule)

        # Check for classes wrapped by decorators returning a function (ex. Singleton)
        i = 0
        while i < len(functions_check):
            name, obj = functions_check[i]
            if obj.__closure__ is not None and len(obj.__closure__) > 0:
                cell = obj.__closure__[0].cell_contents
                if inspect.isclass(cell) and inspect.getsource(cell)[0] == '@':
                    classes_check.append((name, obj))
                    functions_check.pop(i)
                    i -= 1
            i += 1
        classes = {name: {"doc": inspect.getdoc(obj)} for name, obj in classes_check}
        functions = {name: {"doc": inspect.getdoc(obj)} for name, obj in functions_check if not name.startswith("_")}
        builtins = {name: {"doc": inspect.getdoc(obj)} for name, obj in builtins_check if not name.startswith("_")}
        submodules = {name: {"doc": inspect.getdoc(obj)} for name, obj in submodules_check if not (name.startswith("_") or name == "tests" or name == "test")}

        if module_all:
            classes = {_class: _class_elem for _class, _class_elem in classes.items() if _class in module_all}
            functions = {func: func_elem for func, func_elem in functions.items() if func in module_all}
            builtins = {builtin: builtin_elem for builtin, builtin_elem in builtins.items() if builtin in module_all}
            submodules = {submod: submod_elem for submod, submod_elem in submodules.items() if submod in module_all}

        for class_name, class_obj in classes_check:
            methods = {name: {"doc": inspect.getdoc(obj)} for name, obj in inspect.getmembers(class_obj, predicate=inspect.isroutine) if not name.startswith("_")}
            if module_all:
                if class_name in module_all:
                    classes[class_name]["methods"] = methods
            else:
                classes[class_name]["methods"] = methods

        output[m] = {"id": m_id, "doc": doc}
        output[m]["classes"] = classes
        output[m]["functions"] = functions
        output[m]["builtins"] = builtins
        output[m]["submodules"] = {}

        submodule_import_names = [f"{m}.{subm}" for subm in submodules]
        output[m]["submodules"] = inspect_modules(submodule_import_names)

    return output


def write_json(output, file_path):
    classes_json = json.dumps(output)
    print(f"Writing module inspection results to: {file_path}")
    with open(file_path, "w") as f:
        f.write(classes_json)


if __name__ == "__main__":
    print("Running module inspections")

    modules = sys.argv[1:-1] # first arg is this script, last arg is the output file
    json_output_path = Path(sys.argv[-1])

    if os.name == 'nt':
        os.environ['PXR_USD_WINDOWS_DLL_PATH'] = ' ' # prevent usd from running add_dll_directory twice
        for path in os.getenv('PATH', '').split(os.pathsep):
            if os.path.exists(path) and path != '.':
                os.add_dll_directory(path)

    output = inspect_modules(modules)

    write_json(output, json_output_path)
