import logging
from argparse import ArgumentParser
from pathlib import Path
import numpy as np


def initialize_logger(log_filename, level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    if not logger.handlers:
        log_path = Path(log_filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def initialize_argument_parser():
    argParser = ArgumentParser()
    argParser.add_argument("-t", "--plaintext-modulus", type=int, default=255)
    argParser.add_argument("-a", "--plaintext-a", type=int, default=255)
    argParser.add_argument("-b", "--plaintext-b", type=int, default=255)
    return argParser


def parse_arguments(argParser):
    args = argParser.parse_args()
    plaintext_modulus = args.plaintext_modulus
    plaintext_a = args.plaintext_a
    plaintext_b = args.plaintext_b
    return plaintext_modulus, plaintext_a, plaintext_b


def initialize_inputset(plaintext_modulus):
    return [
        (0, 0),
        (0, plaintext_modulus),
        (plaintext_modulus, 0),
        (plaintext_modulus, plaintext_modulus),
    ]


def create_directories():
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path("circuit").mkdir(parents=True, exist_ok=True)


def inspect_ciphertext(ctxt):
    raw = ctxt.serialize()
    arr = np.frombuffer(raw, dtype=np.uint64)
    return np.array2string(arr, threshold=arr.size), arr.size
