import unittest
import json
from api import lambda_handler  # Ensure this is correctly imported
from moto import mock_aws
import boto3

class TestAPI(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.dynamodb = boto3.client(
            'dynamodb',
            region_name='ap-northeast-1',
            aws_access_key_id='fake_access_key',
            aws_secret_access_key='fake_secret_key'
        )
        self.table_name = 'items'
        self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        # Wait until the table exists
        waiter = self.dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=self.table_name)

    @mock_aws
    def tearDown(self):
        self.dynamodb.delete_table(TableName=self.table_name)

    @mock_aws
    def test_create_item(self):
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'id': '1',
                'name': 'item1'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 201)

    @mock_aws
    def test_get_item(self):
        self.dynamodb.put_item(
            TableName=self.table_name,
            Item={
                'id': {'S': '1'},
                'name': {'S': 'item1'}
            }
        )
        event = {
            'httpMethod': 'GET',
            'pathParameters': {
                'id': '1'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), {
            'id': '1',
            'name': 'item1'
        })

    @mock_aws
    def test_update_item(self):
        self.dynamodb.put_item(
            TableName=self.table_name,
            Item={
                'id': {'S': '1'},
                'name': {'S': 'item1'}
            }
        )
        event = {
            'httpMethod': 'PUT',
            'pathParameters': {
                'id': '1'
            },
            'body': json.dumps({
                'name': 'item2'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), {
            'id': '1',
            'name': 'item2'
        })

    @mock_aws
    def test_delete_item(self):
        self.dynamodb.put_item(
            TableName=self.table_name,
            Item={
                'id': {'S': '1'},
                'name': {'S': 'item1'}
            }
        )
        event = {
            'httpMethod': 'DELETE',
            'pathParameters': {
                'id': '1'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Item deleted')

    @mock_aws
    def test_item_not_found(self):
        event = {
            'httpMethod': 'GET',
            'pathParameters': {
                'id': '123'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'Item not found')

if __name__ == '__main__':
    unittest.main()
