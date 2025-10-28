#!/bin/bash

# Build script for FastAPI Docker image
# Usage: ./build.sh [options]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="fastapi-app"
IMAGE_TAG="latest"
DOCKERFILE="Dockerfile"
BUILD_CONTEXT="."

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--tag)
      IMAGE_TAG="$2"
      shift 2
      ;;
    -n|--name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    --no-cache)
      NO_CACHE="--no-cache"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  -t, --tag TAG         Set image tag (default: latest)"
      echo "  -n, --name NAME       Set image name (default: fastapi-app)"
      echo "  --no-cache            Build without using cache"
      echo "  -h, --help            Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_warning "docker-compose is not installed. You can still use 'docker build' manually."
fi

# Display build information
print_info "Building Docker image..."
print_info "Image name: ${IMAGE_NAME}"
print_info "Image tag: ${IMAGE_TAG}"
print_info "Dockerfile: ${DOCKERFILE}"
print_info "Build context: ${BUILD_CONTEXT}"

# Build the Docker image
print_info "Starting build process..."
docker build ${NO_CACHE} \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f "${DOCKERFILE}" \
    "${BUILD_CONTEXT}"

if [ $? -eq 0 ]; then
    print_info "✓ Build completed successfully!"
    print_info "Image: ${IMAGE_NAME}:${IMAGE_TAG}"

    # Display image info
    docker images "${IMAGE_NAME}:${IMAGE_TAG}"

    echo ""
    print_info "To run the container, use:"
    echo "  docker run -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
    print_info "Or use docker-compose:"
    echo "  docker-compose up -d"
    echo ""
    print_info "To push to a registry:"
    echo "  docker tag ${IMAGE_NAME}:${IMAGE_TAG} <registry>/${IMAGE_NAME}:${IMAGE_TAG}"
    echo "  docker push <registry>/${IMAGE_NAME}:${IMAGE_TAG}"
else
    print_error "Build failed!"
    exit 1
fi

