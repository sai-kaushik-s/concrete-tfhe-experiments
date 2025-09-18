import io
import sys
import time
from datetime import datetime

import numpy as np
from concrete import fhe

from common import (
    create_directories,
    initialize_argument_parser,
    initialize_inputset,
    initialize_logger,
    parse_arguments,
)


@fhe.compiler({"x": "encrypted", "y": "encrypted"})
def add(x, y):
    return x + y


def inspect_ciphertext(ctxt):
    raw = ctxt.serialize()
    arr = np.frombuffer(raw, dtype=np.uint64)
    return arr


if __name__ == "__main__":
    create_directories()

    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    log_filename = f"logs/repeated_add_log_{timestamp}.txt"

    logger = initialize_logger(log_filename)
    logger.info("Starting FHE repeated addition script to observe noise growth...")

    argParser = initialize_argument_parser()
    plaintext_modulus, initial_value, value_to_add = parse_arguments(argParser)
    logger.info(
        "Arguments: plaintext_modulus=%s, initial_value=%s, value_to_add=%s",
        plaintext_modulus,
        initial_value,
        value_to_add,
    )

    string_io_buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = string_io_buffer
    try:
        addCircuit = add.compile(
            initialize_inputset(plaintext_modulus), show_statistics=True
        )
    finally:
        sys.stdout = original_stdout
    compiler_stats = string_io_buffer.getvalue()

    logger.info("Circuit successfully compiled.")
    logger.info("Compiler statistics:\n%s", compiler_stats)

    logger.info(
        "Encrypting initial accumulator with %d and the constant with %d.",
        initial_value,
        value_to_add,
    )

    ciphertexts = addCircuit.encrypt(initial_value, value_to_add)
    if ciphertexts is None:
        raise ValueError("Encryption failed, got None")
    if isinstance(ciphertexts, tuple):
        ciphertext_accumulator, ciphertext_addend = ciphertexts
    else:
        ciphertext_accumulator, ciphertext_addend = ciphertexts, None

    expected_sum = initial_value
    iteration = 0

    logger.info("=" * 60)
    logger.info("Starting repeated addition loop to observe noise growth...")
    logger.info("=" * 60)

    start_time = time.time()

    while True:
        iteration += 1

        ciphertext_accumulator = addCircuit.run(
            ciphertext_accumulator, ciphertext_addend
        )

        expected_sum += value_to_add
        decrypted_result = addCircuit.decrypt(ciphertext_accumulator)

        if decrypted_result == expected_sum:
            logger.info(
                "Iteration %3d: OK | Expected: %-5d | Decrypted: %-5d",
                iteration,
                expected_sum,
                decrypted_result,
            )
        else:
            total_time = time.time() - start_time
            logger.info(
                "Iteration %3d: FAIL | Expected: %-5d | Decrypted: %-5d",
                iteration,
                expected_sum,
                decrypted_result,
            )

            logger.info("-" * 60)
            logger.error(
                "MISMATCH DETECTED! The noise has grown too large, causing a decryption error."
            )
            logger.info(
                "A total of %d successful additions were performed.",
                iteration - 1,
            )
            logger.info(
                "Total time for loop: %.4f seconds.",
                total_time,
            )
            logger.info("-" * 60)
            break

        # if iteration >= 2000:
        #     logger.warning("Safety break: Reached 2000 iterations. Exiting.")
        #     break
