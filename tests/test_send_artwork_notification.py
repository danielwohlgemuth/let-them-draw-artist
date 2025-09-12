"""Unit tests for the send_artwork_notification function."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import send_artwork_notification


class TestSendArtworkNotification:
    """Test cases for the send_artwork_notification function."""

    @patch('lambda_function.get_user_email')
    @patch('lambda_function.ses')
    def test_send_notification_success(self, mock_ses, mock_get_user_email):
        """Test successfully sending artwork notification."""
        mock_get_user_email.return_value = 'user@example.com'
        mock_ses.send_templated_email.return_value = {'MessageId': 'msg-123'}

        send_artwork_notification('user-123', 'https://example.com/artwork.png')

        # Verify get_user_email was called
        mock_get_user_email.assert_called_once_with('user-123')

        # Verify SES email was sent
        mock_ses.send_templated_email.assert_called_once_with(
            Source='test@example.com',
            Destination={'ToAddresses': ['user@example.com']},
            Template='ArtworkNotification',
            TemplateData='{"artworkUrl": "https://example.com/artwork.png"}',
            ConfigurationSetName='test-config-set'
        )

    @patch('lambda_function.get_user_email')
    @patch('lambda_function.ses')
    def test_send_notification_different_artwork_url(self, mock_ses, mock_get_user_email):
        """Test sending notification with different artwork URL."""
        mock_get_user_email.return_value = 'test@example.com'
        mock_ses.send_templated_email.return_value = {'MessageId': 'msg-456'}

        artwork_url = 'https://s3.amazonaws.com/bucket/artwork/user-456/request-789.png'
        send_artwork_notification('user-456', artwork_url)

        # Verify template data contains correct artwork URL
        call_args = mock_ses.send_templated_email.call_args
        expected_template_data = f'{{"artworkUrl": "{artwork_url}"}}'
        assert call_args[1]['TemplateData'] == expected_template_data

    @patch('lambda_function.get_user_email')
    @patch('lambda_function.ses')
    def test_send_notification_get_user_email_failure(self, mock_ses, mock_get_user_email):
        """Test when get_user_email fails."""
        mock_get_user_email.side_effect = ValueError("User email not found")

        # Should not raise exception, should print error
        with patch('builtins.print') as mock_print:
            send_artwork_notification('user-123', 'https://example.com/artwork.png')

            # Verify error was printed
            mock_print.assert_called()
            assert any("Failed to send notification" in str(call) for call in mock_print.call_args_list)

        # Verify SES was not called
        mock_ses.send_templated_email.assert_not_called()

    @patch('lambda_function.get_user_email')
    @patch('lambda_function.ses')
    def test_send_notification_ses_failure(self, mock_ses, mock_get_user_email):
        """Test when SES send_templated_email fails."""
        mock_get_user_email.return_value = 'user@example.com'
        mock_ses.send_templated_email.side_effect = Exception("SES error")

        # Should not raise exception, should print error
        with patch('builtins.print') as mock_print:
            send_artwork_notification('user-123', 'https://example.com/artwork.png')

            # Verify error was printed
            mock_print.assert_called()
            assert any("Failed to send notification" in str(call) for call in mock_print.call_args_list)

    @patch('lambda_function.get_user_email')
    @patch('lambda_function.ses')
    def test_send_notification_template_data_format(self, mock_ses, mock_get_user_email):
        """Test that template data is properly formatted as JSON."""
        mock_get_user_email.return_value = 'user@example.com'
        mock_ses.send_templated_email.return_value = {'MessageId': 'msg-123'}

        artwork_url = 'https://example.com/artwork.png'
        send_artwork_notification('user-123', artwork_url)

        # Verify template data is valid JSON
        call_args = mock_ses.send_templated_email.call_args
        template_data = call_args[1]['TemplateData']

        import json
        parsed_data = json.loads(template_data)
        assert parsed_data['artworkUrl'] == artwork_url

    @patch('lambda_function.get_user_email')
    @patch('lambda_function.ses')
    def test_send_notification_configuration_set(self, mock_ses, mock_get_user_email):
        """Test that correct configuration set is used."""
        mock_get_user_email.return_value = 'user@example.com'
        mock_ses.send_templated_email.return_value = {'MessageId': 'msg-123'}

        send_artwork_notification('user-123', 'https://example.com/artwork.png')

        # Verify configuration set name
        call_args = mock_ses.send_templated_email.call_args
        assert call_args[1]['ConfigurationSetName'] == 'test-config-set'
