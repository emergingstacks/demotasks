terraform {
  backend "s3" {
    bucket = "tfstates-devops"
    key    = "demotasks/demotasks.tfstate"
    region = "us-east-1"
  }
}