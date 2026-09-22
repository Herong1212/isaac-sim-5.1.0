import argparse
from os.path import abspath, dirname, realpath, join

from idl.parser import parse
from idl.templates.renderer import Renderer, makedirs
from idl.schema import asymmetric
import idl.templates.filters.py

script_path = abspath(dirname(realpath(__file__)))


def generate(src: str, dest: str, client: bool = True, copyright_path: str = None):
    makedirs(dest)
    spec = parse(src, processors=[
        asymmetric.processor(client)
    ])

    copyright_text = []
    if copyright_path:
        print(f"Copyright file: {copyright_path}")
        with open(copyright_path) as copyright_file:
            copyright_text = copyright_file.readlines()

    renderer = Renderer(spec, template_path=join(script_path, "templates"))
    renderer.include_filters(idl.templates.filters.py)
    renderer.render("data.pyi", join(dest, "data.py"), {
        "copyright": copyright_text,
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
    parser.add_argument("--copyright", dest="copyright_path", type=str, required=False,
                        help="Path to the file with the copyright text.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(args.src, args.dest, args.client, args.copyright_path)
