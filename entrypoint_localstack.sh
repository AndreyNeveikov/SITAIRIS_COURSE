#!/bin/bash

aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set region_name $REGION_NAME
aws --endpoint-url $HOSTNAME_EXTERNAL:$PORT_EXTERNAL s3 mb s3://$BUCKET_NAME