"""Integration tests for the process_message function."""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import process_message


class TestProcessMessage:
    """Test cases for the process_message function."""

    @patch('lambda_function.send_artwork_notification')
    @patch('lambda_function.generate_and_upload_artwork')
    @patch('lambda_function.update_request_status')
    @patch('lambda_function.parse_request_data')
    def test_process_message_success(self, mock_parse, mock_update, mock_generate, mock_send):
        """Test successful processing of a message."""
        # Setup mocks
        mock_parse.return_value = ('user-123', 'request-456', 'circle', 'red')
        mock_generate.return_value = 'https://example.com/artwork.png'

        event = {'body': '{"userId": "user-123", "requestId": "request-456"}'}

        process_message(event)

        # Verify all functions were called in correct order
        mock_parse.assert_called_once_with(event)
        mock_update.assert_any_call('user-123', 'request-456', 'in progress')
        mock_generate.assert_called_once_with('user-123', 'request-456', 'circle', 'red')
        mock_update.assert_any_call('user-123', 'request-456', 'done')
        mock_send.assert_called_once_with('user-123', 'https://example.com/artwork.png')

    @patch('lambda_function.send_artwork_notification')
    @patch('lambda_function.generate_and_upload_artwork')
    @patch('lambda_function.update_request_status')
    @patch('lambda_function.parse_request_data')
    def test_process_message_square_artwork(self, mock_parse, mock_update, mock_generate, mock_send):
        """Test processing message for square artwork."""
        # Setup mocks
        mock_parse.return_value = ('user-789', 'request-101', 'square', 'blue')
        mock_generate.return_value = 'https://example.com/square-artwork.png'

        event = {'body': '{"userId": "user-789", "requestId": "request-101"}'}

        process_message(event)

        # Verify generate_and_upload_artwork was called with square parameters
        mock_generate.assert_called_once_with('user-789', 'request-101', 'square', 'blue')

    @patch('lambda_function.send_artwork_notification')
    @patch('lambda_function.generate_and_upload_artwork')
    @patch('lambda_function.update_request_status')
    @patch('lambda_function.parse_request_data')
    def test_process_message_parse_failure(self, mock_parse, mock_update, mock_generate, mock_send):
        """Test when parse_request_data fails."""
        mock_parse.side_effect = ValueError("Invalid request data")

        event = {'body': 'invalid json'}

        with pytest.raises(ValueError, match="Invalid request data"):
            process_message(event)

        # Verify other functions were not called
        mock_update.assert_not_called()
        mock_generate.assert_not_called()
        mock_send.assert_not_called()

    @patch('lambda_function.send_artwork_notification')
    @patch('lambda_function.generate_and_upload_artwork')
    @patch('lambda_function.update_request_status')
    @patch('lambda_function.parse_request_data')
    def test_process_message_generate_failure(self, mock_parse, mock_update, mock_generate, mock_send):
        """Test when generate_and_upload_artwork fails."""
        mock_parse.return_value = ('user-123', 'request-456', 'circle', 'red')
        mock_generate.side_effect = Exception("S3 upload failed")

        event = {'body': '{"userId": "user-123", "requestId": "request-456"}'}

        with pytest.raises(Exception, match="S3 upload failed"):
            process_message(event)

        # Verify status was updated to in progress but not to done
        mock_update.assert_called_once_with('user-123', 'request-456', 'in progress')
        mock_send.assert_not_called()

    @patch('lambda_function.send_artwork_notification')
    @patch('lambda_function.generate_and_upload_artwork')
    @patch('lambda_function.update_request_status')
    @patch('lambda_function.parse_request_data')
    def test_process_message_send_notification_failure(self, mock_parse, mock_update, mock_generate, mock_send):
        """Test when send_artwork_notification fails (should not raise exception)."""
        mock_parse.return_value = ('user-123', 'request-456', 'circle', 'red')
        mock_generate.return_value = 'https://example.com/artwork.png'

        event = {'body': '{"userId": "user-123", "requestId": "request-456"}'}

        # Should not raise exception even if notification fails
        process_message(event)

        # Verify all functions were called
        mock_parse.assert_called_once_with(event)
        mock_update.assert_any_call('user-123', 'request-456', 'in progress')
        mock_generate.assert_called_once_with('user-123', 'request-456', 'circle', 'red')
        mock_update.assert_any_call('user-123', 'request-456', 'done')
        mock_send.assert_called_once_with('user-123', 'https://example.com/artwork.png')

    @patch('lambda_function.send_artwork_notification')
    @patch('lambda_function.generate_and_upload_artwork')
    @patch('lambda_function.update_request_status')
    @patch('lambda_function.parse_request_data')
    def test_process_message_update_status_failure(self, mock_parse, mock_update, mock_generate, mock_send):
        """Test when update_request_status fails."""
        mock_parse.return_value = ('user-123', 'request-456', 'circle', 'red')
        mock_update.side_effect = Exception("DynamoDB update failed")

        event = {'body': '{"userId": "user-123", "requestId": "request-456"}'}

        with pytest.raises(Exception, match="DynamoDB update failed"):
            process_message(event)

        # Verify other functions were not called after the failure
        mock_generate.assert_not_called()
        mock_send.assert_not_called()
