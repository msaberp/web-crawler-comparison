# Parallel Web Crawler Comparison

This project compares the performance of parallel web crawlers implemented in Go and Python. The crawlers fetch web pages concurrently, extract the page titles, and measure performance metrics.

## Overview

The project consists of two implementations:

1. **Go crawler**: Utilizes goroutines and channels for concurrency
2. **Python crawler**: Uses asyncio and aiohttp for asynchronous operations

Both implementations:
- Read URLs from a shared file (`urls.txt`)
- Fetch web pages concurrently with configurable concurrency limits
- Extract page titles (from HTML) or handle different content types
- Save results in a structured JSON format
- Provide performance metrics

## Requirements

### Go Crawler
- Go 1.16 or higher

### Python Crawler
- Python 3.7 or higher
- Dependencies:
  - aiohttp
  - beautifulsoup4

## Project Structure

```
├── urls.txt              # List of URLs to crawl
├── generate_urls.py      # Script to generate test URLs
├── Makefile              # Automation for building and running
├── python-crawler/
│   ├── main.py           # Python crawler implementation
│   └── requirements.txt  # Python dependencies
└── go-crawler/
    └── main.go           # Go crawler implementation
```

## Usage

The project includes a Makefile to simplify running and comparing the crawlers.

### Setup

Set up Python dependencies and build the Go crawler:

```bash
make setup
```

### Generating Test URLs

Generate a list of URLs for testing (defaults to 100 URLs):

```bash
make generate-urls
```

For more options:

```bash
python generate_urls.py --help
```

### Running the Crawlers

Run the Python crawler:

```bash
make run-python
```

Run the Go crawler:

```bash
make run-go
```

### Run Both and Compare

Run both crawlers and compare their results:

```bash
make all
```

### Clean Up

Clean up generated files:

```bash
make clean
```

## Manual Execution

### Python Crawler

```bash
cd python-crawler
pip install -r requirements.txt
python main.py [concurrency_limit]
```

### Go Crawler

```bash
cd go-crawler
go build -o crawler main.go
./crawler -workers=[concurrency_limit]
```

## Customization

### Adding More URLs

- Edit the `urls.txt` file directly (one URL per line)
- Use the URL generator with a custom count:
  ```bash
  python generate_urls.py --count 500 --output urls.txt
  ```

### Adjusting Concurrency

Both crawlers accept a parameter to adjust the number of concurrent workers:

- Python: Pass a number as a command-line argument
- Go: Use the `-workers` flag

## Output

Both crawlers generate a JSON file with:

- Overall summary metrics (total time, average time per URL, success/fail counts)
- Detailed results for each URL (title, status, time taken)

## Performance Comparison

The main goal is to compare:

1. **Speed**: Total execution time
2. **Efficiency**: Average time per URL
3. **Stability**: Error handling and success rates
4. **Code simplicity**: How each language approaches concurrency

## License

MIT
