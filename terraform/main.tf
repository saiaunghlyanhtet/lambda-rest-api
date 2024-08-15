module "provider" {
  source = "./provider"
}

module "dynamodb" {
  source = "./dynamodb"
}

module "api" {
  source = "./api"
}

module "apigateway" {
  source = "./apigateway"
}

module "iam" {
  source = "./iam"
}
