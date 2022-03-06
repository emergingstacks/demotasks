data aws_vpc "default_vpc"{
  id = "vpc-dbc30ba6"
}
resource "aws_ecs_cluster" "demo-ecs-cluster" {
  name = "ecs-cluster-for-demo"
}
resource "aws_ecs_task_definition" "demoapi_task" {
   family = "ecs-task-def-demo"
   cpu = "256"
   memory = "512"
   requires_compatibilities = ["FARGATE"]
   network_mode = "awsvpc"
   execution_role_arn = aws_iam_role.demo_api_task_execution_role.arn
   container_definitions = <<EOF
[
{
      "name": "sun-api",
      "image": "745946109524.dkr.ecr.us-east-1.amazonaws.com/democi:latest",
      "portMappings": [
        {
          "containerPort": 8080
        }
      ]
}
]
EOF

}

resource "aws_ecs_service" "demoapi_service" {
  name            = "demoapi"
  cluster = aws_ecs_cluster.demo-ecs-cluster.id
  task_definition = aws_ecs_task_definition.demoapi_task.arn
  launch_type = "FARGATE"
  network_configuration {
    subnets = ["subnet-1c95297a"]
    assign_public_ip = true
    security_groups = [aws_security_group.demici-sg.id]
  }
  desired_count = 1
}

resource "aws_security_group" "demici-sg" {
  name        = "demici-sg"
  vpc_id      = data.aws_vpc.default_vpc.id

  ingress {
    protocol        = "-1"
    from_port = 0
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}