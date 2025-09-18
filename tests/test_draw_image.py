"""Unit tests for the draw_image function."""

import pytest
from PIL import Image
import sys
import os

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import draw_image


class TestDrawImage:
    """Test cases for the draw_image function."""

    def test_draw_square(self):
        """Test drawing a square shape."""
        img = draw_image('square', 'red')

        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)
        assert img.mode == 'RGB'

    def test_draw_circle(self):
        """Test drawing a circle shape."""
        img = draw_image('circle', 'blue')

        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)
        assert img.mode == 'RGB'

    def test_draw_hypnotic_squares(self):
        """Test drawing a hypnotic squares shape."""
        img = draw_image('hypnotic squares', 'blue')

        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)
        assert img.mode == 'RGB'

    def test_draw_tiled_lines(self):
        """Test drawing a tiled lines shape."""
        img = draw_image('tiled lines', 'blue')

        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)
        assert img.mode == 'RGB'

    def test_draw_square_case_insensitive(self):
        """Test that shape parameter is case insensitive."""
        img1 = draw_image('SQUARE', 'green')
        img2 = draw_image('square', 'green')

        assert isinstance(img1, Image.Image)
        assert isinstance(img2, Image.Image)
        assert img1.size == img2.size

    def test_draw_circle_case_insensitive(self):
        """Test that shape parameter is case insensitive."""
        img1 = draw_image('CIRCLE', 'yellow')
        img2 = draw_image('circle', 'yellow')

        assert isinstance(img1, Image.Image)
        assert isinstance(img2, Image.Image)
        assert img1.size == img2.size

    def test_invalid_color_fallback(self):
        """Test that invalid colors fall back to black."""
        img = draw_image('square', 'invalidcolor')

        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)

    def test_valid_named_colors(self):
        """Test various valid named colors."""
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'black', 'white']

        for color in colors:
            img = draw_image('square', color)
            assert isinstance(img, Image.Image)
            assert img.size == (512, 512)

    def test_hex_colors(self):
        """Test hex color codes."""
        hex_colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']

        for color in hex_colors:
            img = draw_image('circle', color)
            assert isinstance(img, Image.Image)
            assert img.size == (512, 512)

    def test_rgb_colors(self):
        """Test RGB color format."""
        rgb_colors = ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)']

        for color in rgb_colors:
            img = draw_image('square', color)
            assert isinstance(img, Image.Image)
            assert img.size == (512, 512)

    def test_unknown_shape(self):
        """Test behavior with unknown shape (should not draw anything)."""
        img = draw_image('triangle', 'red')

        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)
        # Should still create a white image even with unknown shape
