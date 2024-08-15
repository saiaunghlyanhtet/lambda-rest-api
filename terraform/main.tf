provider "aws" {
  region = "ap-northeast-1"
}

# Variables
variable "create_dynamodb_table" {
  type    = bool
  default = true
}

variable "create_iam_role" {
  type    = bool
  default = true
}

# DynamoDB Table
resource "aws_dynamodb_table" "items_table" {
  count = var.create_dynamodb_table ? 1 : 0

  name     = "items"
  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  billing_mode = "PAY_PER_REQUEST"

  lifecycle {
    prevent_destroy = true
  }
}

# IAM Role
resource "aws_iam_role" "lambda_exec_role" {
  count = var.create_iam_role ? 1 : 0

  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Sid    = "",
        Principal = {
          Service = "lambda.amazonaws.com",
        },
      },
    ],
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
  ]

  lifecycle {
    prevent_destroy = true
  }
}

# Lambda Function
resource "aws_lambda_function" "crud_lambda" {
  filename         = "lambda_function.zip"
  function_name    = "crudLambdaFunction"
  role             = aws_iam_role.lambda_exec_role[0].arn
  handler          = "api.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("lambda_function.zip")
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "crud_api" {
  name        = "crud-api"
  description = "CRUD API"
}

# API Gateway Resource
resource "aws_api_gateway_resource" "items" {
  rest_api_id = aws_api_gateway_rest_api.crud_api.id
  parent_id   = aws_api_gateway_rest_api.crud_api.root_resource_id
  path_part   = "items"
}

# API Gateway Method and Integration for GET
resource "aws_api_gateway_method" "items_get_method" {
  rest_api_id   = aws_api_gateway_rest_api.crud_api.id
  resource_id   = aws_api_gateway_resource.items.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "items_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.crud_api.id
  resource_id             = aws_api_gateway_resource.items.id
  http_method             = aws_api_gateway_method.items_get_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crud_lambda.invoke_arn
}

# API Gateway Method and Integration for POST
resource "aws_api_gateway_method" "items_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.crud_api.id
  resource_id   = aws_api_gateway_resource.items.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "items_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.crud_api.id
  resource_id             = aws_api_gateway_resource.items.id
  http_method             = aws_api_gateway_method.items_post_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crud_lambda.invoke_arn
}

# API Gateway Method and Integration for PUT
resource "aws_api_gateway_method" "items_put_method" {
  rest_api_id   = aws_api_gateway_rest_api.crud_api.id
  resource_id   = aws_api_gateway_resource.items.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "items_put_integration" {
  rest_api_id             = aws_api_gateway_rest_api.crud_api.id
  resource_id             = aws_api_gateway_resource.items.id
  http_method             = aws_api_gateway_method.items_put_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crud_lambda.invoke_arn
}

# API Gateway Method and Integration for DELETE
resource "aws_api_gateway_method" "items_delete_method" {
  rest_api_id   = aws_api_gateway_rest_api.crud_api.id
  resource_id   = aws_api_gateway_resource.items.id
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "items_delete_integration" {
  rest_api_id             = aws_api_gateway_rest_api.crud_api.id
  resource_id             = aws_api_gateway_resource.items.id
  http_method             = aws_api_gateway_method.items_delete_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crud_lambda.invoke_arn
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crud_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.crud_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.items_get_integration,
    aws_api_gateway_integration.items_post_integration,
    aws_api_gateway_integration.items_put_integration,
    aws_api_gateway_integration.items_delete_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.crud_api.id
  stage_name  = "prod"
}

# Outputs
output "lambda_function_name" {
  value = aws_lambda_function.crud_lambda.function_name
}

output "api_gateway_url" {
  value = "${aws_api_gateway_rest_api.crud_api.execution_arn}/prod/items"
}
