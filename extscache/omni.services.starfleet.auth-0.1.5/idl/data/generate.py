import argparse
from os.path import abspath, dirname, realpath, join

from idl.parser import parse
from idl.templates.renderer import Renderer, makedirs
from idl.schema import asymmetric
import idl.templates.filters.py

script_path = abspath(dirname(realpath(__file__)))


def generate(src: str, dest: str, client: bool = True):
    makedirs(dest)
    spec = parse(src, processors=[
        asymmetric.processor(client)
    ])

    renderer = Renderer(spec, template_path=join(script_path, "templates"))
    renderer.include_filters(idl.templates.filters.py)
    renderer.render("data.pyi", join(dest, "data.py"), {
        "asymmetric": {
            "client": client
        }
    })


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src", dest="src", type=str, required=True,
                        help="Path to specification JSON.")
    parser.add_argument("-d", "--dest", dest="dest", type=str, required=True,
                        help="Path where the generated files will be placed.")
    parser.add_argument("--client", dest="client", type=bool, default=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(args.src, args.dest, args.client)
