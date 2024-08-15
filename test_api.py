import unittest
import json
from api import lambda_handler
from moto import mock_aws
import boto3

class TestAPI(unittest.TestCase):
    
    @mock_aws
    def setUp(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
        self.table_name = 'items'
        self.table = self.dynamodb.create_table(
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
            },
        )
        self.table.wait_until_exists()
        
    @mock_aws
    def tearDown(self):
        self.table.delete()
        
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
        self.table.put_item(
            Item={
                'id': '1',
                'name': 'item1'
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
        self.table.update_item(
            Item={
                'id': '1',
                'name': 'item1'
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
        self.table.put_item(
            Item={
                'id': '1',
                'name': 'item1'
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