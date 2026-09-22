import argparse
from os.path import join, abspath, dirname, realpath

import idl.schema.asymmetric
import idl.templates.filters
import idl.templates.filters.capabilities
import idl.templates.filters.py
from idl.parser import parse
from idl.templates.renderer import mkdir, Renderer

script_path = abspath(dirname(realpath(__file__)))
root_path = abspath(join(script_path, "..", ".."))


def generate_python_client(src: str, dest: str, data_templates: str = None):
    if not data_templates:
        data_templates = join(root_path, "idl", "data", "templates")

    print(f"Data templates: {data_templates}")
    spec = parse(src, processors=[
        idl.schema.asymmetric.processor(client=True)
    ])

    mkdir(dest)
    renderer = Renderer(spec, template_path=[
        join(script_path, "templates"),
        data_templates
    ])
    renderer.include_filters(idl.templates.filters)
    renderer.include_filters(idl.templates.filters.py)
    renderer.include_filters(idl.templates.filters.capabilities)
    renderer.render("client.pyi", join(dest, "client.py"))
    renderer.render("data.pyi", join(dest, "data.py"), {
        "asymmetric": {
            "client": True
        }
    })


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-s", "--src", "--spec", dest="src", type=str, required=True, help="Path to IDL JSON.")
    parser.add_argument("-d", "--dest", "--out", dest="dest", type=str, required=True, help="Output file.")

    # The generator needs to know where the packages are located to import it and copy some
    # files from there into the destination folder.
    parser.add_argument("--data-templates", dest="data_templates", type=str, help="Path to data templates.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_python_client(
        args.src, args.dest,
        args.data_templates,
    )
