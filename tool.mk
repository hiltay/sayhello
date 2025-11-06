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

# Color output
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_RESET := \033[0m

# ============================================================
# Main Installation Target
# ============================================================

.PHONY: install
install: setup-env ## Install SayHello tool
	@echo "$(COLOR_GREEN)✓ SayHello installation complete$(COLOR_RESET)"

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
		echo "$(COLOR_YELLOW)Warning: pyproject.toml not found$(COLOR_RESET)"; \
		exit 1; \
	fi

# ============================================================
# Utility Targets
# ============================================================

.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning SayHello build artifacts..."
	@rm -rf $(TOOL_DIR)/uv.lock
	@rm -rf $(TOOL_DIR)/.venv
	@rm -rf $(TOOL_DIR)/src/sayhello.egg-info
	@echo "$(COLOR_GREEN)✓ Clean complete$(COLOR_RESET)"

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

