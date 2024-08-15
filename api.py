import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table_name = 'items'
table = dynamodb.Table(table_name, region_name='ap-northeast-1')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'GET':
        return get_item(event);
    elif http_method == 'POST':
        return create_item(event);
    elif http_method == 'PUT':
        return update_item(event);
    elif http_method == 'DELETE':
        return delete_item(event);
    else:
        return {
            'statusCode': 405,
            'body': json.dumps('Method Not Allowed')
        }

def get_item(event):
    item_id = event['pathParameters']['id']
    try:
        response = table.get_item(
            Key={
                'id': item_id
            }
        )
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
    else:
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'])
        }
        
def create_item(event):
    item = json.loads(event['body'])
    try:
        table.put_item(
            Item=item
        )
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
    else:
        return {
            'statusCode': 201,
            'body': json.dumps('Item created')
        }

def update_item(event):
    item_id = event['pathParameters']['id']
    item = json.loads(event['body'])
    try:
        table.update_item(
            Key={
                'id': item_id
            },
            UpdateExpression='SET name = :name',
            ExpressionAttributeValues={
                ':name': item['name'],
            }
        )
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Item updated')
        }
        
def delete_item(event):
    item_id = event['pathParameters']['id']
    try:
        table.delete_item(
            Key={
                'id': item_id
            }
        )
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Item deleted')
        }

    