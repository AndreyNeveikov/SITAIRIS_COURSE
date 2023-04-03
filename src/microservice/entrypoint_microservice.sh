#!/bin/bash

function rabbitmq_healthcheck {
  response=$(curl -s -o /dev/null -w "%{http_code}" http://rabbitmq3:15672)
  if [ "$response" = 200 ]; then
    return 0
  else
    return 1
  fi
}

while ! rabbitmq_healthcheck; do
  echo "RabbitMQ is not ready. Waiting for 5 seconds..."
  sleep 5
done

echo "RabbitMQ is ready! Starting microservice."

uvicorn main:app --host 0.0.0.0 --port 8001
