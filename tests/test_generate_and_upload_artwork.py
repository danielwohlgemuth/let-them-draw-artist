"""Unit tests for the generate_and_upload_artwork function."""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import io

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import generate_and_upload_artwork


class TestGenerateAndUploadArtwork:
    """Test cases for the generate_and_upload_artwork function."""

    @patch('lambda_function.s3')
    @patch('lambda_function.draw_image')
    def test_generate_and_upload_square(self, mock_draw_image, mock_s3):
        """Test generating and uploading a square artwork."""
        # Mock the image
        mock_image = Mock()
        mock_draw_image.return_value = mock_image

        # Mock S3 operations
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'https://example.com/artwork.png'

        # Mock image save
        mock_image.save = Mock()

        result = generate_and_upload_artwork('user-123', 'request-456', 'square', 'red')

        # Verify draw_image was called with correct parameters
        mock_draw_image.assert_called_once_with('square', 'red')

        # Verify S3 put_object was called
        mock_s3.put_object.assert_called_once()
        put_call_args = mock_s3.put_object.call_args
        assert put_call_args[1]['Bucket'] == 'test-bucket'  # From mock_env_vars
        assert put_call_args[1]['Key'] == 'artwork/user-123/request-456.png'
        assert put_call_args[1]['ContentType'] == 'image/png'

        # Verify presigned URL generation
        mock_s3.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'test-bucket', 'Key': 'artwork/user-123/request-456.png'},
            ExpiresIn=3600
        )

        # Verify return value
        assert result == 'https://example.com/artwork.png'

    @patch('lambda_function.s3')
    @patch('lambda_function.draw_image')
    def test_generate_and_upload_circle(self, mock_draw_image, mock_s3):
        """Test generating and uploading a circle artwork."""
        # Mock the image
        mock_image = Mock()
        mock_draw_image.return_value = mock_image

        # Mock S3 operations
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'https://example.com/circle-artwork.png'

        # Mock image save
        mock_image.save = Mock()

        result = generate_and_upload_artwork('user-789', 'request-101', 'circle', 'blue')

        # Verify draw_image was called with correct parameters
        mock_draw_image.assert_called_once_with('circle', 'blue')

        # Verify S3 key format
        put_call_args = mock_s3.put_object.call_args
        assert put_call_args[1]['Key'] == 'artwork/user-789/request-101.png'

        # Verify return value
        assert result == 'https://example.com/circle-artwork.png'

    @patch('lambda_function.s3')
    @patch('lambda_function.draw_image')
    def test_s3_key_format(self, mock_draw_image, mock_s3):
        """Test that S3 key is formatted correctly."""
        # Mock the image
        mock_image = Mock()
        mock_draw_image.return_value = mock_image

        # Mock S3 operations
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'https://example.com/test.png'

        # Mock image save
        mock_image.save = Mock()

        generate_and_upload_artwork('test-user', 'test-request', 'square', 'green')

        # Verify S3 key format
        put_call_args = mock_s3.put_object.call_args
        expected_key = 'artwork/test-user/test-request.png'
        assert put_call_args[1]['Key'] == expected_key

    @patch('lambda_function.s3')
    @patch('lambda_function.draw_image')
    def test_image_save_format(self, mock_draw_image, mock_s3):
        """Test that image is saved in PNG format."""
        # Mock the image
        mock_image = Mock()
        mock_draw_image.return_value = mock_image

        # Mock S3 operations
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'https://example.com/test.png'

        # Mock image save
        mock_image.save = Mock()

        generate_and_upload_artwork('user-123', 'request-456', 'square', 'red')

        # Verify image save was called with PNG format
        mock_image.save.assert_called_once()
        save_call_args = mock_image.save.call_args
        assert save_call_args[1]['format'] == 'PNG'

    @patch('lambda_function.s3')
    @patch('lambda_function.draw_image')
    def test_presigned_url_expiration(self, mock_draw_image, mock_s3):
        """Test that presigned URL has correct expiration time."""
        # Mock the image
        mock_image = Mock()
        mock_draw_image.return_value = mock_image

        # Mock S3 operations
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'https://example.com/test.png'

        # Mock image save
        mock_image.save = Mock()

        generate_and_upload_artwork('user-123', 'request-456', 'square', 'red')

        # Verify presigned URL expiration
        presigned_call_args = mock_s3.generate_presigned_url.call_args
        assert presigned_call_args[1]['ExpiresIn'] == 3600
