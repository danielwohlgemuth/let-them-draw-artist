"""Unit tests for the get_user_email function."""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import get_user_email


class TestGetUserEmail:
    """Test cases for the get_user_email function."""

    def test_get_user_email_success(self):
        """Test successfully retrieving user email."""
        mock_response = {
            'UserAttributes': [
                {'Name': 'sub', 'Value': 'user-123'},
                {'Name': 'email', 'Value': 'test@example.com'},
                {'Name': 'name', 'Value': 'Test User'}
            ]
        }

        with patch('lambda_function.cognito') as mock_cognito:
            mock_cognito.admin_get_user.return_value = mock_response

            email = get_user_email('user-123')

            assert email == 'test@example.com'
            mock_cognito.admin_get_user.assert_called_once_with(
                UserPoolId='test-user-pool',
                Username='user-123'
            )

    def test_get_user_email_not_found(self):
        """Test when user email is not found in attributes."""
        mock_response = {
            'UserAttributes': [
                {'Name': 'sub', 'Value': 'user-123'},
                {'Name': 'name', 'Value': 'Test User'}
                # Missing email attribute
            ]
        }

        with patch('lambda_function.cognito') as mock_cognito:
            mock_cognito.admin_get_user.return_value = mock_response

            with pytest.raises(ValueError, match="User email not found"):
                get_user_email('user-123')

    def test_get_user_email_empty_attributes(self):
        """Test when user has no attributes."""
        mock_response = {
            'UserAttributes': []
        }

        with patch('lambda_function.cognito') as mock_cognito:
            mock_cognito.admin_get_user.return_value = mock_response

            with pytest.raises(ValueError, match="User email not found"):
                get_user_email('user-123')

    def test_get_user_email_multiple_emails(self):
        """Test when user has multiple email attributes (should return first one)."""
        mock_response = {
            'UserAttributes': [
                {'Name': 'sub', 'Value': 'user-123'},
                {'Name': 'email', 'Value': 'first@example.com'},
                {'Name': 'email_verified', 'Value': 'true'},
                {'Name': 'email', 'Value': 'second@example.com'}
            ]
        }

        with patch('lambda_function.cognito') as mock_cognito:
            mock_cognito.admin_get_user.return_value = mock_response

            email = get_user_email('user-123')

            # Should return the first email found
            assert email == 'first@example.com'

    def test_get_user_email_different_user_pool_id(self):
        """Test with different user pool ID."""
        mock_response = {
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }

        with patch('lambda_function.cognito') as mock_cognito:
            mock_cognito.admin_get_user.return_value = mock_response

            get_user_email('user-456')

            mock_cognito.admin_get_user.assert_called_once_with(
                UserPoolId='test-user-pool',
                Username='user-456'
            )

    def test_get_user_email_cognito_exception(self):
        """Test when Cognito raises an exception."""
        with patch('lambda_function.cognito') as mock_cognito:
            mock_cognito.admin_get_user.side_effect = Exception("Cognito error")

            with pytest.raises(Exception, match="Cognito error"):
                get_user_email('user-123')
