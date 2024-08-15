resource "aws_dynamodb_table" "items_table" {
  name         = "items"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}
