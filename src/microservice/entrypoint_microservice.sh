#!/bin/bash

until wget -O /dev/null http://admin:admin@rabbitmq3:15672/api/aliveness-test/%2F;
  do echo RabbitMQ is not ready. Waiting for 5 seconds...; sleep 2; done;

echo "RabbitMQ is ready! Starting microservice."

uvicorn main:app --host 0.0.0.0 --port 8001
