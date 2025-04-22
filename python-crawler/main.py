#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import sys
import os
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

async def fetch_url(session, url, semaphore):
    """Fetch a URL and extract its title."""
    start_time = time.time()
    domain = urlparse(url).netloc
    
    try:
        # Use semaphore to limit concurrency
        async with semaphore:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        title = soup.title.string if soup.title else "No title found"
                    else:
                        # For non-HTML responses, like JSON
                        if 'application/json' in content_type:
                            data = await response.json()
                            title = f"JSON Response: {len(str(data))} characters"
                        else:
                            title = f"Non-HTML content: {content_type}"
                    
                    end_time = time.time()
                    return {
                        "url": url,
                        "title": title.strip() if isinstance(title, str) else str(title),
                        "status": response.status,
                        "time_taken": end_time - start_time,
                        "domain": domain
                    }
                else:
                    return {
                        "url": url,
                        "title": f"Error: HTTP {response.status}",
                        "status": response.status,
                        "time_taken": time.time() - start_time,
                        "domain": domain
                    }
    except asyncio.TimeoutError:
        return {
            "url": url,
            "title": "Error: Timeout",
            "status": -1,
            "time_taken": time.time() - start_time,
            "domain": domain
        }
    except Exception as e:
        return {
            "url": url,
            "title": f"Error: {str(e)}",
            "status": -1,
            "time_taken": time.time() - start_time,
            "domain": domain
        }

async def crawl_urls(urls, max_concurrency=10):
    """Crawl a list of URLs concurrently with a limit on concurrency."""
    semaphore = asyncio.Semaphore(max_concurrency)
    
    # Custom session with connection pooling and timeout settings
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=max_concurrency)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch_url(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

def load_urls(filename):
    """Load URLs from a file, one URL per line."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def save_results(results, filename):
    """Save results to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    # Get the urls.txt file from the parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    urls_file = os.path.join(parent_dir, 'urls.txt')
    
    # Check if file exists
    if not os.path.exists(urls_file):
        print(f"Error: URLs file not found at {urls_file}")
        sys.exit(1)
    
    # Load URLs
    urls = load_urls(urls_file)
    print(f"Loaded {len(urls)} URLs")
    
    # Get max concurrency from command line or use default
    max_concurrency = 10
    if len(sys.argv) > 1:
        try:
            max_concurrency = int(sys.argv[1])
        except ValueError:
            print(f"Invalid concurrency value: {sys.argv[1]}. Using default: 10")
    
    print(f"Starting crawl with max concurrency: {max_concurrency}")
    
    # Time the execution
    start_time = time.time()
    
    # Run the crawler
    results = asyncio.run(crawl_urls(urls, max_concurrency))
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Add summary info
    summary = {
        "total_urls": len(urls),
        "successful_fetches": sum(1 for r in results if r["status"] == 200),
        "failed_fetches": sum(1 for r in results if r["status"] != 200),
        "total_time": total_time,
        "average_time_per_url": total_time / len(urls) if urls else 0,
    }
    
    # Print summary
    print(f"\nCrawl Summary:")
    print(f"Total URLs processed: {summary['total_urls']}")
    print(f"Successful fetches: {summary['successful_fetches']}")
    print(f"Failed fetches: {summary['failed_fetches']}")
    print(f"Total time: {summary['total_time']:.2f} seconds")
    print(f"Average time per URL: {summary['average_time_per_url']:.4f} seconds")
    
    # Save results
    results_file = os.path.join(current_dir, 'python_results.json')
    combined_results = {
        "summary": summary,
        "results": results
    }
    save_results(combined_results, results_file)
    print(f"Results saved to {results_file}")

if __name__ == "__main__":
    main()
