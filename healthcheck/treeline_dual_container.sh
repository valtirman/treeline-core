#!/bin/bash

set -e

# -------- CONFIG --------
AWS_REGION="us-east-2"
ECR_ACCOUNT="447711209865"
CLUSTER_NAME="treeline-runtime"
SERVICE_NAME="treeline-proxy-v1"
TG_ARN="arn:aws:elasticloadbalancing:us-east-2:447711209865:targetgroup/treeline-proxy-tg/d1ee717dca2a0a12"

# Paths
PROXY_IMAGE_NAME="treeline-proxy"
HEALTH_IMAGE_NAME="treeline-health"
PROXY_DIR="$(pwd)/../sidecar/proxy"
HEALTH_DIR="$(pwd)"
TASK_DEF_FILE="/tmp/treeline-taskdef.json"

# -------- STEP 1: Build and Push Proxy Container --------
echo "> Building proxy container..."
docker build -t $PROXY_IMAGE_NAME $PROXY_DIR
docker tag $PROXY_IMAGE_NAME $ECR_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$PROXY_IMAGE_NAME:latest
docker push $ECR_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$PROXY_IMAGE_NAME:latest

# -------- STEP 2: Build and Push Health Container --------
echo "> Building health container..."
docker build -t $HEALTH_IMAGE_NAME $HEALTH_DIR
docker tag $HEALTH_IMAGE_NAME $ECR_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$HEALTH_IMAGE_NAME:latest
docker push $ECR_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$HEALTH_IMAGE_NAME:latest

# -------- STEP 3: Generate ECS Task Definition --------
echo "> Creating task definition JSON..."
cat > $TASK_DEF_FILE <<EOF
{
  "family": "$PROXY_IMAGE_NAME",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::$ECR_ACCOUNT:role/TreelineECSExecutionRole",
  "containerDefinitions": [
    {
      "name": "treeline-proxy",
      "image": "$ECR_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$PROXY_IMAGE_NAME:latest",
      "essential": true,
      "portMappings": [{ "containerPort": 8080 }],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/treeline-proxy",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    },
    {
      "name": "treeline-health",
      "image": "$ECR_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$HEALTH_IMAGE_NAME:latest",
      "essential": false,
      "portMappings": [{ "containerPort": 8081 }],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/treeline-health",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# -------- STEP 4: Register Task Definition --------
echo "> Registering ECS task definition..."
REVISION=$(aws ecs register-task-definition \
  --cli-input-json file://$TASK_DEF_FILE \
  --region $AWS_REGION \
  --query 'taskDefinition.revision' \
  --output text)

echo "> Registered revision: $REVISION"

# -------- STEP 5: Update ECS Service --------
echo "> Updating ECS service to use new revision..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $SERVICE_NAME \
  --task-definition $PROXY_IMAGE_NAME:$REVISION \
  --force-new-deployment \
  --region $AWS_REGION

# -------- STEP 6: Update ALB Health Check to port 8081 --------
echo "> Updating ALB health check port to 8081..."
aws elbv2 modify-target-group \
  --target-group-arn $TG_ARN \
  --health-check-port "8081" \
  --region $AWS_REGION

echo ">✅ Deployment complete. ALB should now pass health checks on port 8081."
