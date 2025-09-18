import io
import sys
import time
from datetime import datetime

from concrete import fhe

from common import (
    initialize_argument_parser,
    parse_arguments,
    initialize_logger,
    initialize_inputset,
    create_directories,
    inspect_ciphertext,
)


@fhe.compiler({"x": "encrypted", "y": "encrypted"})
def multiply(x, y):
    return x * y


if __name__ == "__main__":
    create_directories()

    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    log_filename = f"logs/multiply_log_{timestamp}.txt"

    logger = initialize_logger(log_filename)
    logger.info("Starting FHE script...")

    argParser = initialize_argument_parser()
    plaintext_modulus, plaintext_a, plaintext_b = parse_arguments(argParser)
    logger.info(
        "Arguments: plaintext_modulus=%s, plaintext_a=%s, plaintext_b=%s",
        plaintext_modulus,
        plaintext_a,
        plaintext_b,
    )

    string_io_buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = string_io_buffer

    try:
        multiplyCircuit = multiply.compile(
            initialize_inputset(plaintext_modulus), show_statistics=True
        )
    finally:
        sys.stdout = original_stdout

    compiler_stats = string_io_buffer.getvalue()

    destination = f"circuit/multiply_{timestamp}.png"
    drawing = multiplyCircuit.draw(save_to=destination)
    logger.info("Circuit drawing saved to %s", destination)

    mlir_destination = f"circuit/multiply_{timestamp}.mlir"
    with open(mlir_destination, "w", encoding="utf-8") as f:
        f.write(multiplyCircuit.mlir)
    logger.info("MLIR saved to %s", mlir_destination)

    ciphertexts = multiplyCircuit.encrypt(plaintext_a, plaintext_b)
    if ciphertexts is None:
        raise ValueError("Encryption failed, got None")
    if isinstance(ciphertexts, tuple):
        ciphertext_a, ciphertext_b = ciphertexts
    else:
        ciphertext_a, ciphertext_b = ciphertexts, None

    logger.info("Encryption successful for a=%s, b=%s", plaintext_a, plaintext_b)
    ciphertext_a_str, ciphertext_a_size = inspect_ciphertext(ciphertext_a)
    ciphertext_b_str, ciphertext_b_size = inspect_ciphertext(ciphertext_b)
    logger.info("Size of ciphertext a: %d", ciphertext_a_size)
    logger.info("Size of ciphertext b: %d", ciphertext_b_size)

    st = time.time_ns()
    ciphertext_result = multiplyCircuit.run(ciphertext_a, ciphertext_b)
    pt = (time.time_ns() - st) / 1e9
    ciphertext_result_str, ciphertext_result_size = inspect_ciphertext(
        ciphertext_result
    )
    logger.info("Size of ciphertext result: %d", ciphertext_result_size)
    logger.info("Time to compute the multiplication: %.6fs", pt)

    result = multiplyCircuit.decrypt(ciphertext_result)
    logger.info("Decryption result: %s", result)
    assert (
        result == plaintext_a * plaintext_b
    ), "Decrypted result does not match expected value"
    logger.info("Decrypted result matches expected value.")

    logger.info("Compiler statistics:\n%s", compiler_stats)

    logger.info("Ciphertext details:")
    logger.info("Ciphertext a:\n%s", ciphertext_a_str)
    logger.info("Ciphertext b:\n%s", ciphertext_b_str)
    logger.info("Ciphertext result:\n%s", ciphertext_result_str)
