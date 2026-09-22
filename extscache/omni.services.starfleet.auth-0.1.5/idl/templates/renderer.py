import os
import shutil
from typing import Union, List

import jinja2.filters
from idl.spec import Spec
import idl.templates.filters

Templates = Union[str, List[str]]


class Renderer(jinja2.Environment):
    def __init__(self, spec: Spec = None, template_path: Templates = "templates", **kwargs):
        self.overwrite_if_same = True
        overwrite_if_same_param = 'overwrite_if_same'
        if overwrite_if_same_param in kwargs:
            value = kwargs[overwrite_if_same_param]
            self.overwrite_if_same = value if isinstance(value, bool) else False
            kwargs.pop(overwrite_if_same_param, None)

        super().__init__(
            loader=jinja2.FileSystemLoader(searchpath=template_path),
            **kwargs
        )
        self.spec = spec
        self.include_filters(idl.templates.filters)

    def render(self, template: str, out: str, context: dict = None):
        if context is None:
            context = {}

        if self.spec:
            context.setdefault("interfaces", self.spec.interfaces)
            context.setdefault("structs", self.spec.structs)
            context.setdefault("consts", self.spec.consts)
            context.setdefault("enums", self.spec.enums)
            context.setdefault("unions", self.spec.unions)
            context.setdefault("aliases", self.spec.aliases)
            context.setdefault("types", self.spec.types)
            context.setdefault("custom", self.spec.custom)
            context.setdefault("spec", self.spec)

        template = self.get_template(template)
        data = template.render(**context)

        write = self.overwrite_if_same
        if not write:
            try:
                with open(out, "r") as file:
                    file_data = file.read()
                    write = file_data != data
            except OSError:
                write = True

        if write:
            with open(out, "w+") as file:
                file.write(data)

    def include_filters(self, module):
        self.filters.update(module.include(self.spec))


def ignore(exc_types):
    def ignored(func):
        def dec(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (*exc_types, ):
                pass
        return dec
    return ignored


@ignore([FileExistsError])
def copytree(*args, **kwargs):
    return shutil.copytree(*args, **kwargs)


@ignore([FileExistsError])
def mkdir(*args, **kwargs):
    return os.mkdir(*args, **kwargs)


@ignore([FileExistsError])
def makedirs(*args, **kwargs):
    return os.makedirs(*args, **kwargs)


@ignore([shutil.SameFileError])
def copy(src, target, overwrite=False):
    if overwrite or not os.path.exists(target):
        shutil.copy(src, target)
