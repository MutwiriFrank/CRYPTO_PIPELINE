#!/bin/bash
# Create directories and set permissions
mkdir -p /opt/bitnami/spark/{work,temp}
chown -R 1001:1001 /opt/bitnami/spark/{work,temp}

# Start Spark worker with proper arguments
exec /opt/bitnami/scripts/spark/entrypoint.sh /opt/bitnami/scripts/spark/run.sh