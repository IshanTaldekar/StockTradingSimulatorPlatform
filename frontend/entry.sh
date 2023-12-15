#!/bin/bash

# Start Gunicorn
gunicorn -b 0.0.0.0:8000 app:app &

# Start Nginx
service nginx restart
