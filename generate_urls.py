#!/usr/bin/env python3
"""
Script to generate a larger list of URLs for testing the crawler.
This script will create a file with 100-1000 URLs combining:
1. Wikipedia articles
2. HTTPBin endpoints
3. Popular websites
"""

import random
import argparse

# Base URLs for generation
WIKIPEDIA_BASE = "https://en.wikipedia.org/wiki/"
HTTPBIN_BASE = "https://httpbin.org/"

# Wikipedia article titles (partial list)
WIKIPEDIA_ARTICLES = [
    "Algorithm", "Computer_science", "Programming_language", "Artificial_intelligence",
    "Machine_learning", "Data_science", "Computer_network", "Database", "Cloud_computing",
    "Cybersecurity", "Operating_system", "Web_development", "Software_engineering",
    "Internet_of_things", "Virtual_reality", "Augmented_reality", "Quantum_computing",
    "Blockchain", "Cryptography", "Big_data", "Robotics", "Automation", "Computer_vision",
    "Natural_language_processing", "Neural_network", "Deep_learning", "Reinforcement_learning",
    "Computer_architecture", "Computer_graphics", "Human–computer_interaction",
    "Information_theory", "Computer_security", "Software_testing", "Web_browser",
    "Web_server", "Search_engine", "World_Wide_Web", "Internet_Protocol", "TCP/IP",
    "HTTP", "HTTPS", "HTML", "CSS", "JavaScript", "XML", "JSON", "API",
    "REST", "SOAP", "GraphQL", "Microservices", "Containers", "Docker", "Kubernetes",
    "Serverless_computing", "DevOps", "Continuous_integration", "Continuous_delivery",
    "Unix", "Linux", "Microsoft_Windows", "macOS", "Android_(operating_system)",
    "iOS", "Internet_Explorer", "Google_Chrome", "Mozilla_Firefox", "Safari_(web_browser)"
]

# HTTPBin endpoints
HTTPBIN_ENDPOINTS = [
    "get", "post", "put", "delete", "patch", "ip", "user-agent", "headers",
    "uuid", "status/200", "status/404", "status/500", "delay/1", "html",
    "json", "image/png", "image/jpeg", "robots.txt", "xml", "anything"
]

# Popular websites
POPULAR_WEBSITES = [
    "https://github.com",
    "https://stackoverflow.com",
    "https://news.ycombinator.com",
    "https://reddit.com",
    "https://example.com",
    "https://mozilla.org",
    "https://developer.mozilla.org",
    "https://medium.com",
    "https://dev.to",
    "https://go.dev"
]

def generate_urls(count=100):
    """Generate a list of URLs for testing."""
    urls = []
    
    # Add some popular websites
    urls.extend(POPULAR_WEBSITES)
    
    # Add Wikipedia articles
    wikipedia_count = min(count // 2, len(WIKIPEDIA_ARTICLES))
    selected_articles = random.sample(WIKIPEDIA_ARTICLES, wikipedia_count)
    urls.extend([WIKIPEDIA_BASE + article for article in selected_articles])
    
    # Add HTTPBin endpoints
    httpbin_count = min(count // 4, len(HTTPBIN_ENDPOINTS))
    selected_endpoints = random.sample(HTTPBIN_ENDPOINTS, httpbin_count)
    urls.extend([HTTPBIN_BASE + endpoint for endpoint in selected_endpoints])
    
    # If we still need more URLs, create duplicates with query params
    remaining = count - len(urls)
    if remaining > 0:
        base_urls = urls.copy()
        for i in range(remaining):
            base_url = random.choice(base_urls)
            # Add random query parameters
            query_param = f"?param{i}={random.randint(1, 1000)}"
            urls.append(base_url + query_param)
    
    # Shuffle the URLs
    random.shuffle(urls)
    
    # Return only the requested count
    return urls[:count]

def main():
    parser = argparse.ArgumentParser(description='Generate URLs for crawler testing')
    parser.add_argument('--count', type=int, default=100, 
                        help='Number of URLs to generate (default: 100)')
    parser.add_argument('--output', type=str, default='urls.txt',
                        help='Output file name (default: urls.txt)')
    
    args = parser.parse_args()
    
    urls = generate_urls(args.count)
    
    # Write URLs to file
    with open(args.output, 'w') as f:
        for url in urls:
            f.write(f"{url}\n")
    
    print(f"Generated {len(urls)} URLs and saved to {args.output}")

if __name__ == "__main__":
    main() 