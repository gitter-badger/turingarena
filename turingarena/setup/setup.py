import os
import shutil

from turingarena.common import write_to_file
from turingarena.protocol.proxy.python import do_generate_proxy
from turingarena.protocol.skeleton import generate_skeleton
from turingarena.setup.common import *


def _prepare_protocol(dest_dir, protocol_name, source_dir):
    module_dir = _prepare_module_dir(dest_dir, PROTOCOL_QUALIFIER, protocol_name)
    parts = parse_module_name(protocol_name)
    dest_source_filename = os.path.join(module_dir, "_source.tap")
    shutil.copy(
        os.path.join(source_dir, *parts[:-1], f"{parts[-1]}.tap"),
        dest_source_filename,
    )
    with open(dest_source_filename) as f:
        protocol_def = f.read()
    protocol = compile_protocol(protocol_def)
    with open(os.path.join(module_dir, "_proxy.py"), "w") as proxy_module_file:
        write_to_file(do_generate_proxy(protocol), proxy_module_file)
    generate_skeleton(protocol, dest_dir=os.path.join(module_dir, "_skeletons"))


def _prepare_module_dir(dest_dir, qualifier, name):
    module_dir = os.path.join(
        dest_dir,
        *python_module_parts(qualifier, name),
    )
    os.makedirs(module_dir, exist_ok=True)
    with open(os.path.join(module_dir, "__init__.py"), "x"):
        pass
    return module_dir