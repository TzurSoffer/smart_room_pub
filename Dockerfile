# Use a lightweight Python image as the base
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy application files to the container
COPY ./src /app

RUN groupadd -r mosquitto && useradd -r -g mosquitto mosquitto
# Create necessary directories and assign ownership
RUN mkdir -p /var/run/mosquitto /var/log/mosquitto \
    && chown mosquitto:mosquitto /var/run/mosquitto \
    && chown mosquitto:mosquitto /var/log/mosquitto

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends screen mosquitto portaudio19-dev gcc libgl1-mesa-glx libglib2.0-0 avrdude

COPY ./mqttConf.conf /etc/mosquitto/mosquitto.conf

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the run.sh script to the container
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Expose ports (adjust if needed for your MQTT or other services)
EXPOSE 1883

# Run the script
CMD ["/app/run.sh"]
