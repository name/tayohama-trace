echo "deploying traceroute using docker compose"

# Run Docker Compose to deploy Portainer from scratch
docker compose up -d --build

# Tidy up any unused Docker images
docker image prune -f

echo "traceroute deployed"