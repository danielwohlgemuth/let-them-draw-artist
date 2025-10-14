"""Unit tests for the parse_request_data function."""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import parse_request_data


class TestParseRequestData:
    """Test cases for the parse_request_data function."""

    def test_parse_valid_request(self, sample_dynamodb_item):
        """Test parsing a valid request."""
        event = {
            'body': json.dumps({
                'userId': 'test-user-123',
                'requestId': 'test-request-456'
            })
        }

        with patch('lambda_function.table') as mock_table:
            mock_table.get_item.return_value = {'Item': sample_dynamodb_item}

            user_id, request_id, shape, color = parse_request_data(event)

            assert user_id == 'test-user-123'
            assert request_id == 'test-request-456'
            assert shape == 'circle'
            assert color == 'red'

    def test_parse_request_with_different_requirements(self):
        """Test parsing request with different shape and color."""
        event = {
            'body': json.dumps({
                'userId': 'user-789',
                'requestId': 'request-101'
            })
        }

        dynamodb_item = {
            'requestId': 'request-101',
            'userId': 'user-789',
            'requirements': {
                'shape': 'square',
                'color': 'blue'
            }
        }

        with patch('lambda_function.table') as mock_table:
            mock_table.get_item.return_value = {'Item': dynamodb_item}

            user_id, request_id, shape, color = parse_request_data(event)

            assert user_id == 'user-789'
            assert request_id == 'request-101'
            assert shape == 'square'
            assert color == 'blue'

    def test_parse_request_missing_user_id(self):
        """Test parsing request with missing userId."""
        event = {
            'body': json.dumps({
                'requestId': 'test-request-456'
            })
        }

        with pytest.raises(KeyError):
            parse_request_data(event)

    def test_parse_request_missing_request_id(self):
        """Test parsing request with missing requestId."""
        event = {
            'body': json.dumps({
                'userId': 'test-user-123'
            })
        }

        with pytest.raises(KeyError):
            parse_request_data(event)

    def test_parse_request_invalid_json(self):
        """Test parsing request with invalid JSON."""
        event = {
            'body': 'invalid json'
        }

        with pytest.raises(json.JSONDecodeError):
            parse_request_data(event)

    def test_parse_request_missing_requirements(self):
        """Test parsing request when DynamoDB item is missing requirements."""
        event = {
            'body': json.dumps({
                'userId': 'test-user-123',
                'requestId': 'test-request-456'
            })
        }

        dynamodb_item = {
            'requestId': 'test-request-456',
            'userId': 'test-user-123'
            # Missing requirements
        }

        with patch('lambda_function.table') as mock_table:
            mock_table.get_item.return_value = {'Item': dynamodb_item}

            with pytest.raises(KeyError):
                parse_request_data(event)

    def test_parse_request_missing_shape(self):
        """Test parsing request when requirements is missing shape."""
        event = {
            'body': json.dumps({
                'userId': 'test-user-123',
                'requestId': 'test-request-456'
            })
        }

        dynamodb_item = {
            'requestId': 'test-request-456',
            'userId': 'test-user-123',
            'requirements': {
                'color': 'red'
                # Missing shape
            }
        }

        with patch('lambda_function.table') as mock_table:
            mock_table.get_item.return_value = {'Item': dynamodb_item}

            with pytest.raises(KeyError):
                parse_request_data(event)

    def test_parse_request_missing_color(self):
        """Test parsing request when requirements is missing color."""
        event = {
            'body': json.dumps({
                'userId': 'test-user-123',
                'requestId': 'test-request-456'
            })
        }

        dynamodb_item = {
            'requestId': 'test-request-456',
            'userId': 'test-user-123',
            'requirements': {
                'shape': 'circle'
                # Missing color
            }
        }

        with patch('lambda_function.table') as mock_table:
            mock_table.get_item.return_value = {'Item': dynamodb_item}

            with pytest.raises(KeyError):
                parse_request_data(event)
