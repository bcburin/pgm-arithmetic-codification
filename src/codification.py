from pathlib import Path

import numpy as np
from decimal import Decimal, getcontext

from src.pgm import PGMImage

getcontext().prec = 50


def split_image(image: PGMImage, block_size):
    height, width = image.size
    blocks = []
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            block = image.pixels[y:y+block_size, x:x+block_size]
            blocks.append(block)
    return blocks


def calculate_frequencies(block):
    values, counts = np.unique(block, return_counts=True)
    frequencies = {value: count for value, count in zip(values, counts)}
    return frequencies


def binary_arithmetic_encoding(block, frequencies):
    total_count = sum(frequencies.values())
    probabilities = {k: v / total_count
                     for k, v in frequencies.items()}

    low = Decimal(0)
    high = Decimal(1)

    for value in block.flatten():
        range_width = high - low
        high = low + range_width * \
            Decimal(sum(probabilities[v]
                    for v in sorted(probabilities) if v <= value))
        low = low + range_width * \
            Decimal(sum(probabilities[v]
                    for v in sorted(probabilities) if v < value))

    code = (low + high) / Decimal(2)
    return code


def encode_image_to_file(image: PGMImage, block_size):
    blocks = split_image(image, block_size)
    results = []
    for block in blocks:
        frequencies = calculate_frequencies(block)
        code = binary_arithmetic_encoding(block, frequencies)
        results.append((code, frequencies))
    return results


def binary_arithmetic_decoding(code, frequencies, block_size):
    total_count = sum(frequencies.values())
    probabilities = {k: v / total_count
                     for k, v in frequencies.items()}
    sorted_values = sorted(probabilities.keys())

    decoded_block = []
    low = Decimal(0)
    high = Decimal(1)

    for _ in range(block_size * block_size):
        range_width = high - low
        scaled_value = (code - low) / range_width

        cumulative_probability = Decimal(0)
        for value in sorted_values:
            next_cumulative_probability = cumulative_probability + \
                Decimal(probabilities[value])
            if cumulative_probability <= scaled_value < next_cumulative_probability:
                decoded_block.append(value)
                high = low + range_width * next_cumulative_probability
                low = low + range_width * cumulative_probability
                break
            cumulative_probability = next_cumulative_probability

    return np.array(decoded_block).reshape((block_size, block_size))


def combine_blocks(blocks, size, block_size):
    image = np.zeros(size, dtype=np.uint8)
    block_idx = 0
    for y in range(0, size[0], block_size):
        for x in range(0, size[1], block_size):
            image[y:y+block_size, x:x+block_size] = blocks[block_idx]
            block_idx += 1
    return image


def encode_results_to_file(image: PGMImage, block_size: int, save_path: Path):
    results = encode_image_to_file(image, block_size)
    with open(save_path, 'w') as f:
        for code, frequencies in results:
            f.write(f'{code}\n')
            f.write(f'{frequencies}\n')


def decode_image_from_file(file_path: Path, block_size, size) -> PGMImage:
    with open(file_path, 'r') as file:
        lines = file.readlines()
    codes = []
    frequencies_list = []
    for i in range(0, len(lines), 2):
        code = Decimal(lines[i].strip())
        frequencies = eval(lines[i+1].strip())
        codes.append(code)
        frequencies_list.append(frequencies)

    blocks = []
    for code, frequencies in zip(codes, frequencies_list):
        blocks.append(binary_arithmetic_decoding(code, frequencies, block_size))
    pixels = combine_blocks(blocks, size, block_size)
    return PGMImage(245, pixels, size)


# if __name__ == '__main__':
#     for i, img in enumerate(read_pgm_images()):
#         results = encode_image_to_file(img, 2)
#         blocks = []
#         for code, frequencies in results:
#             blocks.append(binary_arithmetic_decoding(code, frequencies, 2))
#         pixels = combine_blocks(blocks, img.size, 2)
#         decoded_img = PGMImage(img.max_value, pixels, img.size)
#         decoded_img.write(Path(f'new_out{i}.pgm'))

