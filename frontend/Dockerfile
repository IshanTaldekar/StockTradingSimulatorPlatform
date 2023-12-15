FROM ubuntu:20.04 AS base

# Set the working directory
WORKDIR /home/ubuntu/frontend

# Update the package list and install necessary dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx

# Copy the frontend code to the container
COPY . /home/ubuntu/frontend

# Convert line endings for entry.sh
RUN apt-get update && apt-get install dos2unix -y && dos2unix /home/ubuntu/frontend/entry.sh && chmod +x /home/ubuntu/frontend/entry.sh


# Create a virtual environment and activate it
RUN python3 -m venv venv
RUN /bin/bash -c "source venv/bin/activate"

# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Create SSL directory and set permissions
RUN mkdir -p /etc/nginx/ssl && \
    chmod 700 /etc/nginx/ssl

# Generate self-signed SSL certificate (replace with your own certificate)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=US/ST=NEW YORK/L=NYC/O=NYU/OU=NYU/CN=NYU/emailAddress=palak7693@gmail.com"

# Copy Nginx custom configuration
COPY nginx_custom_config /etc/nginx/sites-available/default

# Create systemd service file
COPY frontendservice.service /etc/systemd/system/frontend.service

# Reload systemd daemon and start frontend service
CMD ["systemctl", "daemon-reload", "&&", "systemctl", "start", "frontend", "&&", "systemctl", "enable", "frontend"]

# Start Gunicorn and Nginx
CMD ["bash", "-c", "chmod +x entry.sh && ./entry.sh"]


# Start Gunicorn and Nginx
#CMD /bin/bash -c "gunicorn -b 0.0.0.0:8000 app:app &  service nginx restart"

# Expose port 80 and 443
EXPOSE 80
EXPOSE 443
