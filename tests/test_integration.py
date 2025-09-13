"""Full integration tests using moto to mock AWS services."""

import pytest
import json
import sys
import os
from unittest.mock import patch
import boto3
from moto import dynamodb, s3, cognitoidentity, ses, ssm

# Add src directory to path to import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import lambda_handler


class TestIntegration:
    """Full integration tests for the lambda function."""

    # @patch.dict(os.environ, {
    #     'TABLE_NAME': 'test-table',
    #     'BUCKET_NAME': 'test-bucket',
    #     'USER_POOL_ID': 'test-user-pool',
    #     'SES_CONFIGURATION_SET': 'test-config-set',
    #     'SES_FROM_EMAIL': 'test@example.com'
    # })
    # def test_full_workflow_success(self):
    #     """Test the complete workflow from SQS event to email notification."""
    #     # Setup AWS services
    #     self._setup_aws_services()

    #     # Create test data
    #     user_id = 'test-user-123'
    #     request_id = 'test-request-456'

    #     # Add item to DynamoDB
    #     self.table.put_item(Item={
    #         'requestId': request_id,
    #         'userId': user_id,
    #         'requirements': {
    #             'shape': 'circle',
    #             'color': 'red'
    #         },
    #         'status': 'pending'
    #     })

    #     # Create SQS event
    #     event = {
    #         'Records': [
    #             {
    #                 'messageId': 'msg-123',
    #                 'body': json.dumps({
    #                     'userId': user_id,
    #                     'requestId': request_id
    #                 })
    #             }
    #         ]
    #     }

    #     context = Mock()

    #     # Execute lambda handler
    #     result = lambda_handler(event, context)

    #     # Verify no failures
    #     assert result == {'batchItemFailures': []}

    #     # Verify DynamoDB item was updated
    #     response = self.table.get_item(Key={'requestId': request_id, 'userId': user_id})
    #     item = response['Item']
    #     assert item['status'] == 'done'
    #     assert 'artwork_url' in item
    #     assert item['artwork_url'].startswith('https://')

    #     # Verify S3 object was created
    #     s3_objects = self.s3.list_objects_v2(Bucket='test-bucket')
    #     assert 'Contents' in s3_objects
    #     assert len(s3_objects['Contents']) == 1
    #     assert s3_objects['Contents'][0]['Key'] == f'artwork/{user_id}/{request_id}.png'

    # @patch.dict(os.environ, {
    #     'TABLE_NAME': 'test-table',
    #     'BUCKET_NAME': 'test-bucket',
    #     'USER_POOL_ID': 'test-user-pool',
    #     'SES_CONFIGURATION_SET': 'test-config-set',
    #     'SES_FROM_EMAIL': 'test@example.com'
    # })
    # def test_full_workflow_square_artwork(self):
    #     """Test the complete workflow with square artwork."""
    #     # Setup AWS services
    #     self._setup_aws_services()

    #     # Create test data
    #     user_id = 'test-user-789'
    #     request_id = 'test-request-101'

    #     # Add item to DynamoDB
    #     self.table.put_item(Item={
    #         'requestId': request_id,
    #         'userId': user_id,
    #         'requirements': {
    #             'shape': 'square',
    #             'color': 'blue'
    #         },
    #         'status': 'pending'
    #     })

    #     # Create SQS event
    #     event = {
    #         'Records': [
    #             {
    #                 'messageId': 'msg-456',
    #                 'body': json.dumps({
    #                     'userId': user_id,
    #                     'requestId': request_id
    #                 })
    #             }
    #         ]
    #     }

    #     context = Mock()

    #     # Execute lambda handler
    #     result = lambda_handler(event, context)

    #     # Verify no failures
    #     assert result == {'batchItemFailures': []}

    #     # Verify DynamoDB item was updated
    #     response = self.table.get_item(Key={'requestId': request_id, 'userId': user_id})
    #     item = response['Item']
    #     assert item['status'] == 'done'
    #     assert 'artwork_url' in item

    # @patch.dict(os.environ, {
    #     'TABLE_NAME': 'test-table',
    #     'BUCKET_NAME': 'test-bucket',
    #     'USER_POOL_ID': 'test-user-pool',
    #     'SES_CONFIGURATION_SET': 'test-config-set',
    #     'SES_FROM_EMAIL': 'test@example.com'
    # })
    # def test_workflow_with_missing_dynamodb_item(self):
    #     """Test workflow when DynamoDB item is missing."""
    #     # Setup AWS services
    #     self._setup_aws_services()

    #     # Create SQS event without corresponding DynamoDB item
    #     event = {
    #         'Records': [
    #             {
    #                 'messageId': 'msg-123',
    #                 'body': json.dumps({
    #                     'userId': 'missing-user',
    #                     'requestId': 'missing-request'
    #                 })
    #             }
    #         ]
    #     }

    #     context = Mock()

    #     # Execute lambda handler
    #     result = lambda_handler(event, context)

    #     # Verify failure
    #     assert result == {'batchItemFailures': [{'itemIdentifier': 'msg-123'}]}

    # @patch.dict(os.environ, {
    #     'TABLE_NAME': 'test-table',
    #     'BUCKET_NAME': 'test-bucket',
    #     'USER_POOL_ID': 'test-user-pool',
    #     'SES_CONFIGURATION_SET': 'test-config-set',
    #     'SES_FROM_EMAIL': 'test@example.com'
    # })
    # def test_workflow_with_invalid_json(self):
    #     """Test workflow with invalid JSON in SQS message."""
    #     # Setup AWS services
    #     self._setup_aws_services()

    #     # Create SQS event with invalid JSON
    #     event = {
    #         'Records': [
    #             {
    #                 'messageId': 'msg-123',
    #                 'body': 'invalid json'
    #             }
    #         ]
    #     }

    #     context = Mock()

    #     # Execute lambda handler
    #     result = lambda_handler(event, context)

    #     # Verify failure
    #     assert result == {'batchItemFailures': [{'itemIdentifier': 'msg-123'}]}

    def _setup_aws_services(self):
        """Setup AWS services for testing."""
        # Setup DynamoDB
        with dynamodb(), s3(), cognitoidentity(), ses(), ssm():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self.table = dynamodb.create_table(
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
            self.s3 = boto3.client('s3', region_name='us-east-1')
            self.s3.create_bucket(Bucket='test-bucket')

            # Setup Cognito
            cognito = boto3.client('cognito-idp', region_name='us-east-1')
            user_pool = cognito.create_user_pool(PoolName='test-pool')
            user_pool_id = user_pool['UserPool']['Id']

            # Create test user
            cognito.admin_create_user(
                UserPoolId=user_pool_id,
                Username='test-user-123',
                UserAttributes=[
                    {'Name': 'email', 'Value': 'test@example.com'},
                    {'Name': 'email_verified', 'Value': 'true'}
                ]
            )

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
