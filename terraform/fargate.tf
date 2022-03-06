resource "aws_ecs_cluster" "demo-ecs-cluster" {
  name = "ecs-cluster-for-demo"
}
resource "aws_ecs_task_definition" "demoapi_task" {
   family = "ecs-task-def-demo"
   cpu = "256"
   memory = "512"
   requires_compatibilities = ["FARGATE"]
   network_mode = "awsvpc"
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
  desired_count = 1
}