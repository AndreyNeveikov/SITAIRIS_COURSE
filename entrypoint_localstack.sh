#!/bin/bash

aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set region_name $REGION_NAME
aws --endpoint-url $HOSTNAME_EXTERNAL:$PORT_EXTERNAL s3 mb s3://$BUCKET_NAME
aws ses verify-email-identity --email-address ${EMAIL_HOST_USER} --endpoint-url=${HOSTNAME_EXTERNAL}:${PORT_EXTERNAL} --region ${REGION_NAME}
curl -o lambda.zip -L "https://drive.google.com/uc?id=1BU-6uDN40s-Fj1jQioDgnXP0b0Zi_5ax&export=download"
aws lambda create-function \
  --function-name handler \
  --runtime python3.8 \
  --zip-file fileb:///opt/code/localstack/lambda.zip \
  --handler handler.handler \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --timeout 10 \
  --region $REGION_NAME --profile default \
  --endpoint-url=${HOSTNAME_EXTERNAL}:${PORT_EXTERNAL}