from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict

from src.pgm import PGMImage
from src.utils import read_pgm_images


class ArithmeticEncoder:
    def __init__(self):
        self.low = 0.0
        self.high = 1.0
        self.precision = 32  # Number of bits of precision for the fractional part
        self.one = 1 << self.precision
        self.half = 1 << (self.precision - 1)
        self.quarter = 1 << (self.precision - 2)
        self.three_quarters = self.one - self.quarter

    @staticmethod
    def _build_probability_table(data: list[int]) -> Dict[int, Tuple[float, float]]:
        frequencies = defaultdict(int)
        for value in data:
            frequencies[value] += 1

        total = sum(frequencies.values())
        probabilities = {k: v / total for k, v in frequencies.items()}

        low = 0.0
        prob_table = {}
        for value, prob in sorted(probabilities.items()):
            high = low + prob
            prob_table[value] = (low, high)
            low = high

        return prob_table

    def encode(self, image: PGMImage) -> float:
        data = [pixel for row in image.pixels for pixel in row]
        prob_table = self._build_probability_table(data)

        low = 0.0
        high = 1.0
        for value in data:
            rng = high - low
            high = low + rng * prob_table[value][1]
            low = low + rng * prob_table[value][0]

            while True:
                if high < 0.5:
                    low *= 2
                    high *= 2
                elif low >= 0.5:
                    low = 2 * (low - 0.5)
                    high = 2 * (high - 0.5)
                elif low >= 0.25 and high < 0.75:
                    low = 2 * (low - 0.25)
                    high = 2 * (high - 0.25)
                else:
                    break

        return (low + high) / 2

    def decode(self, code: float, image: PGMImage) -> PGMImage:
        data = [pixel for row in image.pixels for pixel in row]
        prob_table = self._build_probability_table(data)

        low = 0.0
        high = 1.0
        value = code
        decoded_data = []

        for _ in range(len(data)):
            rng = high - low
            cumulative_value = (value - low) / rng

            for pixel_value, (low_prob, high_prob) in prob_table.items():
                if low_prob <= cumulative_value < high_prob:
                    decoded_data.append(pixel_value)
                    high = low + rng * high_prob
                    low = low + rng * low_prob
                    break

            while True:
                if high < 0.5:
                    low *= 2
                    high *= 2
                    value *= 2
                elif low >= 0.5:
                    low = 2 * (low - 0.5)
                    high = 2 * (high - 0.5)
                    value = 2 * (value - 0.5)
                elif low >= 0.25 and high < 0.75:
                    low = 2 * (low - 0.25)
                    high = 2 * (high - 0.25)
                    value = 2 * (value - 0.25)
                else:
                    break

        decoded_pixels = []
        for i in range(0, len(decoded_data), image.size[0]):
            decoded_pixels.append(decoded_data[i:i + image.size[0]])

        return PGMImage(image.max_value, decoded_pixels, image.size, image.path)


if __name__ == '__main__':
    for idx, img in enumerate(read_pgm_images()):
        coded = ArithmeticEncoder().encode(img)
        decoded_img = ArithmeticEncoder().decode(coded, img)
        decoded_img.write(Path(f'out{idx}.pgm'))
