"""Unit tests for the update_request_status function."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import update_request_status


class TestUpdateRequestStatus:
    """Test cases for the update_request_status function."""

    def test_update_status_only(self):
        """Test updating status without artwork URL."""
        with patch('lambda_function.table') as mock_table:
            update_request_status('user-123', 'request-456', 'in progress')

            mock_table.update_item.assert_called_once()
            call_args = mock_table.update_item.call_args

            assert call_args[1]['Key'] == {'requestId': 'request-456', 'userId': 'user-123'}
            assert call_args[1]['UpdateExpression'] == 'SET #status = :status'
            assert call_args[1]['ExpressionAttributeNames'] == {'#status': 'status'}
            assert call_args[1]['ExpressionAttributeValues'] == {':status': 'in progress'}

    def test_update_status_with_artwork_url(self):
        """Test updating status with artwork URL."""
        artwork_url = 'https://example.com/artwork.png'

        with patch('lambda_function.table') as mock_table:
            update_request_status('user-123', 'request-456', 'done', artwork_url)

            mock_table.update_item.assert_called_once()
            call_args = mock_table.update_item.call_args

            assert call_args[1]['Key'] == {'requestId': 'request-456', 'userId': 'user-123'}
            assert call_args[1]['UpdateExpression'] == 'SET #status = :status, artwork_url = :artwork_url'
            assert call_args[1]['ExpressionAttributeNames'] == {'#status': 'status'}
            assert call_args[1]['ExpressionAttributeValues'] == {
                ':status': 'done',
                ':artwork_url': artwork_url
            }

    def test_update_status_different_statuses(self):
        """Test updating with different status values."""
        statuses = ['pending', 'in progress', 'done', 'failed']

        for status in statuses:
            with patch('lambda_function.table') as mock_table:
                update_request_status('user-123', 'request-456', status)

                call_args = mock_table.update_item.call_args
                assert call_args[1]['ExpressionAttributeValues'][':status'] == status

    def test_update_status_with_none_artwork_url(self):
        """Test updating status with None artwork URL (should not include URL in update)."""
        with patch('lambda_function.table') as mock_table:
            update_request_status('user-123', 'request-456', 'done', None)

            call_args = mock_table.update_item.call_args
            assert call_args[1]['UpdateExpression'] == 'SET #status = :status'
            assert ':artwork_url' not in call_args[1]['ExpressionAttributeValues']

    def test_update_status_with_empty_artwork_url(self):
        """Test updating status with empty string artwork URL."""
        with patch('lambda_function.table') as mock_table:
            update_request_status('user-123', 'request-456', 'done', '')

            call_args = mock_table.update_item.call_args
            assert call_args[1]['UpdateExpression'] == 'SET #status = :status, artwork_url = :artwork_url'
            assert call_args[1]['ExpressionAttributeValues'][':artwork_url'] == ''
