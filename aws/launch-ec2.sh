#!/bin/bash

# Variables
AWS_REGION="us-east-1"
STACK_NAME="resume-coach-stack"
TEMPLATE_PATH="./aws/ec2-template.yaml"  # Relative path from this script
KEY_PAIR_NAME="my-key"  # Must match the key pair name in AWS

# Create the CloudFormation stack
aws cloudformation create-stack \
  --region "$AWS_REGION" \
  --stack-name $STACK_NAME \
  --template-body file://$TEMPLATE_PATH \
  --parameters ParameterKey=KeyName,ParameterValue=$KEY_PAIR_NAME \
  --capabilities CAPABILITY_NAMED_IAM

echo "Stack creation initiated."

echo "Waiting for stack to complete..."
aws cloudformation wait stack-create-complete \
  --stack-name $STACK_NAME \
  --region $AWS_REGION

echo "Stack creation complete. Fetching outputs..."

aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs" \
  --output table