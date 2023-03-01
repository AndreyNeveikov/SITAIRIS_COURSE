#!/bin/bash

cd src/
celery -A innotter worker -l info
