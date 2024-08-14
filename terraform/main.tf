module "provider" {
  source = "./provider.tf"
}

module "dynamodb" {
  source = "./dynamodb.tf"
}

module "api" {
  source = "./api.tf"
}

module "apigateway" {
  source = "./apigateway.tf"
}

module "iam" {
  source = "./iam.tf"
}
