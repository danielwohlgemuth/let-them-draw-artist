#!/usr/bin/env python3
"""
Utility script to test the draw_image function from lambda_function.py

Usage:
    python test_draw_image.py --shape <shape> --color <color>

Example:
    python test_draw_image.py --shape circle --color red
    python test_draw_image.py --shape square --color "#FF5733"
"""

import os
import sys
import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from draw import draw_image


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate an image with the specified shape and color.')
    parser.add_argument('--shape', required=True, help='Shape to draw (e.g., circle, square)')
    parser.add_argument('--color', required=True, help='Color name or hex code (e.g., red, #FF5733)')
    parser.add_argument('--output-dir', default='test_output',
                       help='Directory to save the output images (default: test_output)')
    return parser.parse_args()


def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)


def main():
    args = parse_arguments()

    ensure_dir(args.output_dir)

    try:
        img = draw_image(args.shape, args.color)

        safe_shape = "".join(c if c.isalnum() else "_" for c in args.shape.lower())
        safe_color = "".join(c if c.isalnum() else "_" for c in args.color.lower())
        output_filename = f"{safe_shape}_{safe_color}.png"
        output_path = os.path.join(args.output_dir, output_filename)

        img.save(output_path, 'PNG')
        print(f"Image saved to: {output_path}")

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
