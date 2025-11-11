# SayHello Tool Makefile
#
# This Makefile defines tool-specific setup logic for SayHello.
# It is included by the main tools/deps/Makefile.

# Tool metadata
TOOL_NAME := sayhello
TOOL_VERSION := 1.0.0

# Paths (PROJECT_ROOT is passed from parent Makefile)
TOOL_DIR := $(shell pwd)

# UV settings
UV := uv
UV_SYNC_FLAGS := --index-url https://pypi.tuna.tsinghua.edu.cn/simple
UV_HTTP_TIMEOUT := 300

# Docker settings (passed from parent Makefile)
# DOCKER_REGISTRY, DOCKER_USERNAME, DOCKER_PASSWORD are available
DOCKER_IMAGE := $(DOCKER_REGISTRY)/macroverse/hnet_antibody:latest
DOCKER_CONTAINER_NAME := sayhello_hnet_antibody

# ============================================================
# Main Installation Target
# ============================================================

.PHONY: install
install: setup-env setup-docker ## Install SayHello tool
	@echo "✓ SayHello installation complete"

# ============================================================
# Setup Steps
# ============================================================

.PHONY: setup-env
setup-env: ## Setup Python environment with UV
	@echo "Setting up SayHello environment..."
	@if [ -f "$(TOOL_DIR)/pyproject.toml" ]; then \
		echo "Running uv sync..."; \
		cd $(TOOL_DIR) && UV_HTTP_TIMEOUT=$(UV_HTTP_TIMEOUT) $(UV) sync $(UV_SYNC_FLAGS); \
	else \
		echo "Warning: pyproject.toml not found"; \
		exit 1; \
	fi

.PHONY: setup-docker
setup-docker: ## Setup Docker image and container
	@echo "========================================"
	@echo "Setting up Docker environment"
	@echo "========================================"
	@# Check if Docker is installed
	@if ! command -v docker &> /dev/null; then \
		echo "Warning: Docker not found, skipping Docker setup"; \
		exit 0; \
	fi
	@# Login to Docker registry if password is provided
	@if [ -n "$(DOCKER_PASSWORD)" ] && [ "$(DOCKER_PASSWORD)" != "password" ]; then \
		echo "Logging into Docker registry: $(DOCKER_REGISTRY)"; \
		echo "$(DOCKER_PASSWORD)" | docker login $(DOCKER_REGISTRY) -u $(DOCKER_USERNAME) --password-stdin; \
	else \
		echo "Skipping Docker login (no password configured)"; \
	fi
	@# Pull Docker image
	@echo "Pulling Docker image: $(DOCKER_IMAGE)"; \
	if docker pull $(DOCKER_IMAGE); then \
		echo "✓ Docker image pulled successfully"; \
	else \
		echo "Warning: Failed to pull Docker image"; \
		exit 0; \
	fi
	@# Check if container already exists
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(DOCKER_CONTAINER_NAME)$$"; then \
		echo "Container $(DOCKER_CONTAINER_NAME) already exists"; \
		if docker ps --format '{{.Names}}' | grep -q "^$(DOCKER_CONTAINER_NAME)$$"; then \
			echo "✓ Container is already running"; \
		else \
			echo "Starting existing container..."; \
			docker start $(DOCKER_CONTAINER_NAME); \
		fi; \
	else \
		echo "Creating and starting Docker container: $(DOCKER_CONTAINER_NAME)"; \
		if command -v nvidia-smi &> /dev/null; then \
			echo "GPU detected, starting container with GPU support"; \
			docker run -d -i --name $(DOCKER_CONTAINER_NAME) --gpus all $(DOCKER_IMAGE) tail -f /dev/null; \
		else \
			echo "No GPU detected, starting container without GPU"; \
			docker run -d -i --name $(DOCKER_CONTAINER_NAME) $(DOCKER_IMAGE) tail -f /dev/null; \
		fi; \
		echo "✓ Container started successfully"; \
	fi
	@echo "✓ Docker setup complete"

# ============================================================
# Utility Targets
# ============================================================

.PHONY: clean
clean: clean-docker ## Clean build artifacts
	@echo "Cleaning SayHello build artifacts..."
	@rm -rf $(TOOL_DIR)/uv.lock
	@rm -rf $(TOOL_DIR)/.venv
	@rm -rf $(TOOL_DIR)/src/sayhello.egg-info
	@echo "✓ Clean complete"

.PHONY: clean-docker
clean-docker: ## Clean Docker container and image
	@echo "Cleaning Docker resources..."
	@if command -v docker &> /dev/null; then \
		if docker ps -a --format '{{.Names}}' | grep -q "^$(DOCKER_CONTAINER_NAME)$$"; then \
			echo "Stopping container $(DOCKER_CONTAINER_NAME)..."; \
			docker stop $(DOCKER_CONTAINER_NAME) 2>/dev/null || true; \
			echo "Removing container $(DOCKER_CONTAINER_NAME)..."; \
			docker rm $(DOCKER_CONTAINER_NAME) 2>/dev/null || true; \
			echo "✓ Container removed"; \
		else \
			echo "Container $(DOCKER_CONTAINER_NAME) not found"; \
		fi; \
	fi

.PHONY: test
test: ## Run tests
	@echo "Running SayHello tests..."
	@cd $(TOOL_DIR) && $(UV) run pytest tests/ -v

.PHONY: info
info: ## Show tool information
	@echo "Tool: $(TOOL_NAME)"
	@echo "Version: $(TOOL_VERSION)"
	@echo "Directory: $(TOOL_DIR)"
	@echo "UV: $(shell which $(UV) 2>/dev/null || echo 'not found')"

# ============================================================
# Help
# ============================================================

.PHONY: help
help: ## Show this help
	@echo "SayHello Tool Makefile"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

