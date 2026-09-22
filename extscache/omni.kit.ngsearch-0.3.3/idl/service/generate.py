import argparse
import os

import idl.formatting
import idl.templates.filters
import idl.templates.filters.py
import idl.templates.filters.capabilities
import idl.schema.asymmetric
from idl.parser import parse

from idl.templates.renderer import Renderer, makedirs

script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
root_path = os.path.abspath(os.path.join(script_path, "..", ".."))


def generate_service(json_path: str, output_path: str, data_templates: str = None, copyright_path: str = None):
    if not data_templates:
        data_templates = os.path.join(root_path, "idl", "data", "templates")

    print(f"Data templates: {data_templates}")
    spec = parse(json_path, processors=[
        idl.schema.asymmetric.processor(client=False)
    ])

    copyright_text = []
    if copyright_path:
        print(f"Copyright file: {copyright_path}")
        with open(copyright_path) as copyright_file:
            copyright_text = copyright_file.readlines()

    renderer = Renderer(
        spec=spec,
        template_path=[
            os.path.join(script_path, "templates"),
            data_templates,
        ]
    )
    renderer.include_filters(idl.templates.filters)
    renderer.include_filters(idl.templates.filters.py)
    renderer.include_filters(idl.templates.filters.capabilities)

    makedirs(output_path)
    renderer.render(
        "data.pyi", os.path.join(output_path, "__data__.py"),
        {
            "copyright": copyright_text,
            "asymmetric": {
                "client": False
            }
        }
    )

    for interface in spec.interfaces.values():
        dependencies = list(reversed(idl.parser.interface_dependencies(interface, spec, deep=True)))
        render_interface(interface, dependencies, output_path, renderer, copyright_text)

    print(f"Done. Service is available in {output_path}")


def render_interface(interface, dependencies, output_path, renderer, copyright_text):
    interface_types = idl.parser.group_types(dependencies)
    interface_types["interfaces"] = {interface.name: interface}

    interface_filename = idl.formatting.underscore(interface.name) + ".py"
    interface_path = os.path.join(output_path, interface_filename)

    renderer.render("service.pyi", interface_path, {
        **interface_types,
        "types": dependencies,
        "interface": interface,
        "copyright": copyright_text,
    })


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-s", "--src", dest="src", type=str, required=True, help="Path to the IDL JSON.")
    parser.add_argument("-d", "--dest", dest="dest", type=str, required=True, help="Output folder.")
    parser.add_argument("--copyright", dest="copyright_path", type=str, required=False,
                        help="Path to the file with the copyright text.")

    # The generator needs to know where the packages are located to import it and copy some
    # files from there into the destination folder.
    parser.add_argument("--data-templates", dest="data_templates", type=str,
                        help="Path to templates used for generating data types.")
    return parser.parse_args()


if __name__ == "__main__":
    _args = parse_args()

    generate_service(
        json_path=_args.src,
        output_path=_args.dest,
        data_templates=_args.data_templates,
        copyright_path=_args.copyright_path,
    )
