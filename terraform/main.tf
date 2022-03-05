resource "aws_ecr_repository" "democi" {
  name                 = "democi"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}