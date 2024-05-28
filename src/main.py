from argparse import ArgumentParser
from pathlib import Path

from src.codification import encode_results_to_file, decode_image_from_file
from src.pgm import PGMImage
from src.utils import calculate_compression_rate


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('path', help='path to the image to encode')
    parser.add_argument('--coded-path', help='save path of the code stream',
                        default='coded.txt')
    parser.add_argument('--decoded-path',
                        help='path to save the final decoded image', default='out.pgm')
    parser.add_argument('--block-size', help='block size to use for encoding',
                        default=2)
    parser.add_argument('--precision',
                        help='floating point precision to use codification', default=50)
    return parser


def main():
    args = create_parser().parse_args()
    block_size = int(args.block_size)
    img_path = Path(args.path)
    img = PGMImage.read(file_path=img_path)
    # codification
    coded_path = Path(args.coded_path)
    encode_results_to_file(img, block_size, save_path=coded_path)
    # decodification
    decoded_img = decode_image_from_file(
        file_path=coded_path, block_size=block_size, size=img.size)
    decoded_path = Path(args.decoded_path)
    decoded_img.write(file_path=decoded_path)
    # print compression rate
    compression_rate = calculate_compression_rate(img_path, coded_path)
    print(f'Compression rate: {compression_rate}.')


if __name__ == '__main__':
    main()
