import os
from tempfile import TemporaryDirectory

from turingarena_common.commands import LocalExecutionParameters
from turingarena_impl.cli_server.pack import create_working_directory
from turingarena_impl.evaluation.evaluator import Evaluator


def evaluate(working_directory, evaluator_cmd, submission, local_execution=LocalExecutionParameters.DEFAULT):
    with TemporaryDirectory() as temp_dir:
        files = {}
        for name, submission_file in submission.items():
            dirpath = os.path.join(temp_dir, name)
            os.mkdir(dirpath)
            path = os.path.join(dirpath, submission_file.filename)
            with open(path, "xb") as f:
                f.write(submission_file.content)
            files[name] = path

        yield from evaluate_files(working_directory, evaluator_cmd, files, local_execution)


def evaluate_files(working_directory, evaluator_cmd, files, local_execution=LocalExecutionParameters.DEFAULT):
    with create_working_directory(working_directory, local_execution=local_execution) as work_dir:
        cwd = os.path.join(work_dir, working_directory.current_directory)
        evaluator = Evaluator.get_evaluator(evaluator_cmd, cwd=cwd)
        yield from evaluator.evaluate(files=files)
