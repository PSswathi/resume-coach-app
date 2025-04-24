#!/bin/bash

PEM_FILE=~/keys/my-key.pem
IMAGE_TAR=./aws/resume-coach-app.tar
EC2_IP="<ec2-ip>"

echo "Save the Image to a .tar File"
docker save resume-coach-app:latest -o $IMAGE_TAR

echo "Copying Docker image to EC2..."
scp -i "$PEM_FILE" "$IMAGE_TAR" ec2-user@"$EC2_IP":/home/ec2-user/

echo "Image copied. Now SSH into EC2..."

ssh -i "$PEM_FILE" ec2-user@"$EC2_IP" << EOF
  echo "Loading Docker image..."
  docker load -i resume-coach-app.tar
./
  echo "Running the container..."
  docker run -d -p 8501:8501 resume-coach-app

  echo "Resume Coach app is running at http://$EC2_IP:8501"
EOF