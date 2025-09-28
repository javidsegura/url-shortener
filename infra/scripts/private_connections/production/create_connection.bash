#! /bin/bash

APP_SERVER_NAME="public_web_server"  
DATABASE_NAME="private_database" 
ENVIRONMENT="production"
PROJECT_NAME="url_shortener"
REGION="us-east-1"

echo "Searching for instance with tags:"
echo "  Name: ${APP_SERVER_NAME}"
echo "  Environment: ${ENVIRONMENT}"
echo "  Project: ${PROJECT_NAME}"
echo ""


WEB_SERVER_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=${APP_SERVER_NAME}" \
    "Name=tag:Environment,Values=${ENVIRONMENT}" \
    "Name=tag:Project,Values=${PROJECT_NAME}" \
    --query "Reservations[].Instances[].InstanceId" \
    --region $REGION \
    --output text
)

echo "Found Instance ID: '${WEB_SERVER_ID}'"

if [ -z "$WEB_SERVER_ID" ]; then
    echo "Error: No EC2 instance found with the specified tags."
    exit 1
fi

RDS_ENDPOINT=$(aws rds describe-db-instances \
    --query "DBInstances[?contains(TagList[?Key=='Name'].Value, '${DATABASE_NAME}') && contains(TagList[?Key=='Environment'].Value, '${ENVIRONMENT}') && contains(TagList[?Key=='Project'].Value, '${PROJECT_NAME}')].Endpoint.Address" \
    --region $REGION \
    --output text
)

if [ -z "$RDS_ENDPOINT" ]; then
    echo "Error: No RDS instance found with the specified tags."
    exit 1
fi

echo "Starting SSM port-forwarding session..."
echo "EC2 Instance ID: ${WEB_SERVER_ID}"
echo "RDS Endpoint: ${RDS_ENDPOINT}"

LOCAL_PORT=3307

aws ssm start-session \
      --target $WEB_SERVER_ID \
      --document-name AWS-StartPortForwardingSessionToRemoteHost \
      --parameters "host=[\"${RDS_ENDPOINT}\"], portNumber=[\"3306\"],localPortNumber=[\"${LOCAL_PORT}\"]"\
      --region $REGION
