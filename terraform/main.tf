resource "aws_ecr_repository" "demorepo" {
  name                 = "demorepo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}