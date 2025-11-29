# ================================
# PostPay - Developer Task Runner
# ================================

PYTHON := python3

# ----------------
# Install commands
# ----------------
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install ".[dev]"

# ------
# Run app
# ------
run:
	postpay

# -------
# Testing
# -------
test:
	pytest -v

# -------------
# Lint & Format
# -------------
lint:
	flake8 src/postpay

format:
	black src/postpay

lint-all:
	flake8 .
	black --check .

# ------------------
# Build distribution
# ------------------
build:
	rm -rf dist build
	$(PYTHON) -m build

# -------------
# Clean project
# -------------
clean:
	rm -rf dist build .pytest_cache .mypy_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# ----------------
# Show version
# ----------------
version:
	$(PYTHON) -c "from postpay.version import __version__; print(__version__)"
