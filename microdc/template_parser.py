import jinja2
import os


def readtemplate(template):
    current_path, current_file = os.path.split(__file__)
    template = "{}/templates/{}.jinja2".format(current_path, template)
    try:
        with open(template, 'r') as file:
            data = file.read()
        file.close()
        return data
    except FileNotFoundError:
        raise OSError("cant open {}".format(template))


def parsetemplate(template, **kwargs):
    return jinja2.Environment(trim_blocks=True).from_string(template).render(kwargs).rstrip()
