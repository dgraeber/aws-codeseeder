
from aws_codeseeder import LOGGER, commands
from typing import Optional
import json
import logging
import importlib

DEBUG_LOGGING_FORMAT = "[%(asctime)s][%(filename)-13s:%(lineno)3d] %(message)s"
DEBUG_LOGGING_FORMAT_REMOTE = "[%(filename)-13s:%(lineno)3d] %(message)s"

def set_log_level(level: int, format: Optional[str] = None) -> None:
    kwargs = {"level": level}
    if format:
        kwargs["format"] = format  # type: ignore
    logging.basicConfig(**kwargs)  # type: ignore
    LOGGER.setLevel(level)
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("s3transfer").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)

def execute(args_file: str, debug: bool) -> None:
    if debug:
        set_log_level(level=logging.DEBUG, format=DEBUG_LOGGING_FORMAT)
    else:
        set_log_level(level=logging.INFO, format="%(message)s")
    with open(args_file, "r") as file:
        fn_args = json.load(file)
    LOGGER.info("fn_args: %s", fn_args)
    module_name, func_name = fn_args["fn_id"].split(":")
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    func(*fn_args["args"], **fn_args["kwargs"])


if __name__ == "__main__":
    args_file = '/Users/dgraeber/aws-seed-group/idf-modules/codeseeder.out/permissions-pre-dummy-dummy/bundle/fn_args.json'
    execute(args_file=args_file,debug=True)