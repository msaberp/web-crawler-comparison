.PHONY: all setup run-python run-go compare clean generate-urls

# Default number of workers (can be overridden with make WORKERS=20)
WORKERS ?= 10

# Default target
all: setup run-python run-go compare

# Setup: Install Python dependencies and build Go executable
setup:
	@echo "Setting up Python dependencies..."
	cd python-crawler && pip install -r requirements.txt
	@echo "Building Go crawler..."
	cd go-crawler && go build -o crawler main.go

# Generate URLs
generate-urls:
	@echo "Generating URLs..."
	python generate_urls.py --count 100 --output urls.txt

# Run Python crawler
run-python:
	@echo "Running Python crawler with $(WORKERS) workers..."
	cd python-crawler && python main.py $(WORKERS)

# Run Go crawler
run-go:
	@echo "Running Go crawler with $(WORKERS) workers..."
	cd go-crawler && ./crawler -workers=$(WORKERS)

# Compare results
compare:
	@echo "Comparing results..."
	@echo "========================="
	@echo "PYTHON RESULTS:"
	@echo "========================="
	@cat python-crawler/python_results.json | grep -A5 "summary"
	@echo "========================="
	@echo "GO RESULTS:"
	@echo "========================="
	@cat go-crawler/go_results.json | grep -A5 "summary"
	@echo "========================="
	@echo "Done!"

# Clean up
clean:
	@echo "Cleaning up..."
	rm -f python-crawler/python_results.json
	rm -f go-crawler/go_results.json
	rm -f go-crawler/crawler

# Help
help:
	@echo "Available targets:"
	@echo "  all          - Setup, run both crawlers and compare results (default)"
	@echo "  setup        - Install Python dependencies and build Go executable"
	@echo "  generate-urls- Generate a new list of URLs for testing"
	@echo "  run-python   - Run Python crawler"
	@echo "  run-go       - Run Go crawler"
	@echo "  compare      - Compare the results"
	@echo "  clean        - Clean up generated files"
	@echo "  help         - Show this help"
	@echo ""
	@echo "Variables:"
	@echo "  WORKERS      - Number of concurrent workers (default: 10)"
	@echo "                 Example: make run-python WORKERS=20"