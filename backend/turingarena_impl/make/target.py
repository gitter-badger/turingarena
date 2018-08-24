import os
import sys
from tempfile import TemporaryDirectory

from turingarena_impl.cli_server.git_manager import GitManager
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language

INTERFACE_TXT = "interface.txt"


def create_interface_code_generator(interface_path, code_generator):
    def generator(outfile):
        with open(interface_path) as f:
            interface = InterfaceDefinition.compile(f.read())
        code_generator.generate_to_file(interface, outfile)

    return generator


def generate_interface_targets(dirpath):
    for lang in Language.languages():
        interface_path = os.path.join(dirpath, INTERFACE_TXT)
        yield (
            os.path.join(dirpath, "code", f"skeleton{lang.extension}"),
            create_interface_code_generator(interface_path, lang.skeleton_generator()),
        )
        yield (
            os.path.join(dirpath, "code", f"template{lang.extension}"),
            create_interface_code_generator(interface_path, lang.template_generator()),
        )


def _generate_targets(root):
    for dirpath, dirnames, filenames in os.walk(root):
        if INTERFACE_TXT in filenames:
            yield from generate_interface_targets(os.path.relpath(dirpath, root))


def generate_targets(root):
    return list(_generate_targets(root))


def make_target(outdir, path, generator):
    os.makedirs(os.path.join(outdir, os.path.dirname(path)), exist_ok=True)
    with open(path, "w") as f:
        generator(f)


def make(repositories, packs):
    with TemporaryDirectory() as root:
        git = GitManager(git_dir=None, work_dir=root)
        git.fetch_repositories(repositories)
        git.import_trees(packs)

        targets = generate_targets(root)

        with TemporaryDirectory() as outdir:
            for path, generator in targets:
                with open(os.path.join(outdir, path), "w") as f:
                    generator(f)

            git2 = GitManager(git_dir=None, work_dir=outdir)
            commit_id, tree_id = git2.commit_work()
    return tree_id
