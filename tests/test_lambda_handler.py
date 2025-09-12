"""Integration tests for the lambda_handler function."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import lambda_handler


class TestLambdaHandler:
    """Test cases for the lambda_handler function."""

    @patch('lambda_function.process_message')
    def test_lambda_handler_single_record_success(self, mock_process):
        """Test lambda handler with single successful record."""
        event = {
            'Records': [
                {
                    'messageId': 'msg-123',
                    'body': '{"userId": "user-123", "requestId": "request-456"}'
                }
            ]
        }
        context = Mock()

        result = lambda_handler(event, context)

        # Verify process_message was called
        mock_process.assert_called_once_with(event['Records'][0])

        # Verify no batch item failures
        assert result == {'batchItemFailures': []}

    @patch('lambda_function.process_message')
    def test_lambda_handler_multiple_records_success(self, mock_process):
        """Test lambda handler with multiple successful records."""
        event = {
            'Records': [
                {
                    'messageId': 'msg-123',
                    'body': '{"userId": "user-123", "requestId": "request-456"}'
                },
                {
                    'messageId': 'msg-456',
                    'body': '{"userId": "user-789", "requestId": "request-101"}'
                },
                {
                    'messageId': 'msg-789',
                    'body': '{"userId": "user-101", "requestId": "request-202"}'
                }
            ]
        }
        context = Mock()

        result = lambda_handler(event, context)

        # Verify process_message was called for each record
        assert mock_process.call_count == 3

        # Verify no batch item failures
        assert result == {'batchItemFailures': []}

    @patch('lambda_function.process_message')
    def test_lambda_handler_single_record_failure(self, mock_process):
        """Test lambda handler with single failed record."""
        mock_process.side_effect = Exception("Processing failed")

        event = {
            'Records': [
                {
                    'messageId': 'msg-123',
                    'body': '{"userId": "user-123", "requestId": "request-456"}'
                }
            ]
        }
        context = Mock()

        result = lambda_handler(event, context)

        # Verify process_message was called
        mock_process.assert_called_once_with(event['Records'][0])

        # Verify batch item failure
        expected_failures = [{'itemIdentifier': 'msg-123'}]
        assert result == {'batchItemFailures': expected_failures}

    @patch('lambda_function.process_message')
    def test_lambda_handler_mixed_success_failure(self, mock_process):
        """Test lambda handler with some successful and some failed records."""
        def side_effect(record):
            if record['messageId'] == 'msg-456':
                raise Exception("Processing failed")

        mock_process.side_effect = side_effect

        event = {
            'Records': [
                {
                    'messageId': 'msg-123',
                    'body': '{"userId": "user-123", "requestId": "request-456"}'
                },
                {
                    'messageId': 'msg-456',
                    'body': '{"userId": "user-789", "requestId": "request-101"}'
                },
                {
                    'messageId': 'msg-789',
                    'body': '{"userId": "user-101", "requestId": "request-202"}'
                }
            ]
        }
        context = Mock()

        result = lambda_handler(event, context)

        # Verify process_message was called for each record
        assert mock_process.call_count == 3

        # Verify only failed record is in batch item failures
        expected_failures = [{'itemIdentifier': 'msg-456'}]
        assert result == {'batchItemFailures': expected_failures}

    @patch('lambda_function.process_message')
    def test_lambda_handler_multiple_failures(self, mock_process):
        """Test lambda handler with multiple failed records."""
        def side_effect(record):
            if record['messageId'] in ['msg-123', 'msg-789']:
                raise Exception("Processing failed")

        mock_process.side_effect = side_effect

        event = {
            'Records': [
                {
                    'messageId': 'msg-123',
                    'body': '{"userId": "user-123", "requestId": "request-456"}'
                },
                {
                    'messageId': 'msg-456',
                    'body': '{"userId": "user-789", "requestId": "request-101"}'
                },
                {
                    'messageId': 'msg-789',
                    'body': '{"userId": "user-101", "requestId": "request-202"}'
                }
            ]
        }
        context = Mock()

        result = lambda_handler(event, context)

        # Verify process_message was called for each record
        assert mock_process.call_count == 3

        # Verify failed records are in batch item failures
        expected_failures = [
            {'itemIdentifier': 'msg-123'},
            {'itemIdentifier': 'msg-789'}
        ]
        assert result == {'batchItemFailures': expected_failures}

    @patch('lambda_function.process_message')
    def test_lambda_handler_empty_records(self, mock_process):
        """Test lambda handler with empty records list."""
        event = {'Records': []}
        context = Mock()

        result = lambda_handler(event, context)

        # Verify process_message was not called
        mock_process.assert_not_called()

        # Verify no batch item failures
        assert result == {'batchItemFailures': []}

    @patch('lambda_function.process_message')
    def test_lambda_handler_exception_logging(self, mock_process):
        """Test that exceptions are logged when processing fails."""
        mock_process.side_effect = Exception("Processing failed")

        event = {
            'Records': [
                {
                    'messageId': 'msg-123',
                    'body': '{"userId": "user-123", "requestId": "request-456"}'
                }
            ]
        }
        context = Mock()

        with patch('builtins.print') as mock_print:
            lambda_handler(event, context)

            # Verify exception was logged
            mock_print.assert_called()
            assert any("Processing failed" in str(call) for call in mock_print.call_args_list)
