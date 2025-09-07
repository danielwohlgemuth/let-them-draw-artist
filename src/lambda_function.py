import boto3
import io
import json
import os
import traceback

from PIL import Image, ImageColor, ImageDraw


cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
ses = boto3.client('ses')
ssm = boto3.client('ssm')

TABLE_NAME = os.environ['TABLE_NAME']
BUCKET_NAME = os.environ['BUCKET_NAME']
USER_POOL_ID = os.environ['USER_POOL_ID']
SES_CONFIGURATION_SET = os.environ['SES_CONFIGURATION_SET']
SES_FROM_EMAIL = os.environ['SES_FROM_EMAIL']
FROM_EMAIL = ssm.get_parameter(Name='/let-them-draw/from-email')['Parameter']['Value']

table = dynamodb.Table(TABLE_NAME)

def draw_image(shape, color):
    img = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(img)

    try:
        # https://drafts.csswg.org/css-color-4/#named-colors
        rgb_color = ImageColor.getrgb(color)
    except ValueError:
        rgb_color = (0, 0, 0)

    if shape.lower() == 'square':
        draw.rectangle([100, 100, 300, 300], fill=rgb_color)
    elif shape.lower() == 'circle':
        draw.ellipse([100, 100, 300, 300], fill=rgb_color)

    return img

def parse_request_data(event):
    """Parse request data from the event."""
    body = json.loads(event['body'])
    user_id = body['userId']
    request_id = body['requestId']

    response = table.get_item(Key={'requestId': request_id, 'userId': user_id})
    requirements = response['Item']['requirements']
    shape = requirements['shape']
    color = requirements['color']

    return user_id, request_id, shape, color

def update_request_status(user_id, request_id, status, artwork_url=None):
    """Update the request status in DynamoDB."""
    update_expression = 'SET #status = :status'
    expression_values = {':status': status}

    if artwork_url:
        update_expression += ', artwork_url = :artwork_url'
        expression_values[':artwork_url'] = artwork_url

    table.update_item(
        Key={'requestId': request_id, 'userId': user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues=expression_values
    )

def generate_and_upload_artwork(user_id, request_id, shape, color):
    """Generate artwork image and upload to S3, returning the presigned URL."""
    image = draw_image(shape, color)

    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    s3_key = f"artwork/{user_id}/{request_id}.png"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=img_buffer.getvalue(),
        ContentType='image/png'
    )

    artwork_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600
    )

    return artwork_url

def get_user_email(user_id):
    """Retrieve user email from Cognito."""
    user_response = cognito.admin_get_user(
        UserPoolId=USER_POOL_ID,
        Username=user_id
    )

    for attr in user_response['UserAttributes']:
        if attr['Name'] == 'email':
            return attr['Value']

    raise ValueError("User email not found")

def send_artwork_notification(user_id, artwork_url):
    """Send email notification to user about completed artwork."""
    try:
        user_email = get_user_email(user_id)

        ses.send_templated_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [user_email]},
            Template='ArtworkNotification',
            TemplateData=json.dumps({
                'artworkUrl': artwork_url,
            }),
            ConfigurationSetName=SES_CONFIGURATION_SET
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
        print(traceback.format_exc())

def process_message(event):
    """Process a single artwork request message."""
    user_id, request_id, shape, color = parse_request_data(event)
    print(f"user_id: {user_id}, request_id: {request_id}, shape: {shape}, color: {color}")

    update_request_status(user_id, request_id, 'in progress')

    artwork_url = generate_and_upload_artwork(user_id, request_id, shape, color)

    update_request_status(user_id, request_id, 'done', artwork_url)

    send_artwork_notification(user_id, artwork_url)

def lambda_handler(event, context):
    batch_item_failures = []

    for record in event['Records']:
        try:
            process_message(record)
        except Exception as e:
            print(traceback.format_exc())
            batch_item_failures.append({
                'itemIdentifier': record['messageId']
            })

    return {
        'batchItemFailures': batch_item_failures
    }