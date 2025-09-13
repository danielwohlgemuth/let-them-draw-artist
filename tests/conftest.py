"""Test configuration and fixtures for lambda function tests."""

import os
import json
import pytest
from unittest.mock import Mock, patch
from moto import dynamodb, s3, cognitoidentity, ses, ssm
import boto3


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'TABLE_NAME': 'test-table',
        'BUCKET_NAME': 'test-bucket',
        'USER_POOL_ID': 'test-user-pool',
        'SES_CONFIGURATION_SET': 'test-configuration-set',
        'SES_FROM_EMAIL': 'test@example.com'
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_event():
    """Sample SQS event for testing."""
    return {
        'Records': [
            {
                'messageId': 'test-message-id',
                'body': json.dumps({
                    'userId': 'test-user-123',
                    'requestId': 'test-request-456',
                    'requirements': {
                        'shape': 'circle',
                        'color': 'red'
                    }
                })
            }
        ]
    }


@pytest.fixture
def sample_dynamodb_item():
    """Sample DynamoDB item for testing."""
    return {
        'requestId': 'test-request-456',
        'userId': 'test-user-123',
        'requirements': {
            'shape': 'circle',
            'color': 'red'
        },
        'status': 'pending'
    }


@pytest.fixture
def mock_aws_services():
    """Mock AWS services for testing."""
    with dynamodb(), s3(), cognitoidentity(), ses(), ssm():
        # Setup DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'requestId', 'KeyType': 'HASH'},
                {'AttributeName': 'userId', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'requestId', 'AttributeType': 'S'},
                {'AttributeName': 'userId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Setup S3
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        # Setup Cognito
        cognito = boto3.client('cognito-idp', region_name='us-east-1')
        user_pool = cognito.create_user_pool(PoolName='test-pool')
        user_pool_id = user_pool['UserPool']['Id']

        # Setup SES
        ses = boto3.client('ses', region_name='us-east-1')
        ses.verify_email_identity(EmailAddress='test@example.com')

        # Setup SSM
        ssm = boto3.client('ssm', region_name='us-east-1')
        ssm.put_parameter(
            Name='/let-them-draw/from-email',
            Value='test@example.com',
            Type='String'
        )

        yield {
            'dynamodb': dynamodb,
            'table': table,
            's3': s3,
            'cognito': cognito,
            'user_pool_id': user_pool_id,
            'ses': ses,
            'ssm': ssm
        }


@pytest.fixture
def mock_context():
    """Mock Lambda context for testing."""
    context = Mock()
    context.function_name = 'test-function'
    context.function_version = '1'
    context.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
    context.memory_limit_in_mb = 128
    context.remaining_time_in_millis = lambda: 30000
    return context
