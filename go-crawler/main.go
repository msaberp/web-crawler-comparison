package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
)

// Result represents the crawling result for a URL
type Result struct {
	URL       string  `json:"url"`
	Title     string  `json:"title"`
	Status    int     `json:"status"`
	TimeTaken float64 `json:"time_taken"`
	Domain    string  `json:"domain"`
}

// Summary represents the crawl summary
type Summary struct {
	TotalURLs         int     `json:"total_urls"`
	SuccessfulFetches int     `json:"successful_fetches"`
	FailedFetches     int     `json:"failed_fetches"`
	TotalTime         float64 `json:"total_time"`
	AverageTimePerURL float64 `json:"average_time_per_url"`
}

// CombinedResults contains both the summary and individual results
type CombinedResults struct {
	Summary Summary  `json:"summary"`
	Results []Result `json:"results"`
}

// Worker is a function that processes URLs from the jobs channel and sends results to the results channel
func worker(id int, jobs <-chan string, results chan<- Result, wg *sync.WaitGroup, client *http.Client) {
	defer wg.Done()

	for urlStr := range jobs {
		startTime := time.Now()

		// Parse domain from URL
		parsedURL, err := url.Parse(urlStr)
		domain := ""
		if err == nil {
			domain = parsedURL.Host
		}

		// Try to fetch the URL
		result := fetchURL(urlStr, client, startTime, domain)
		results <- result
	}
}

// Extract title from HTML content
func extractTitle(body string) string {
	titleRegex := regexp.MustCompile(`<title[^>]*>(.*?)</title>`)
	matches := titleRegex.FindStringSubmatch(body)

	if len(matches) > 1 {
		return strings.TrimSpace(matches[1])
	}

	return "No title found"
}

// Fetch a URL and extract its title
func fetchURL(urlStr string, client *http.Client, startTime time.Time, domain string) Result {
	resp, err := client.Get(urlStr)
	if err != nil {
		return Result{
			URL:       urlStr,
			Title:     fmt.Sprintf("Error: %s", err.Error()),
			Status:    -1,
			TimeTaken: time.Since(startTime).Seconds(),
			Domain:    domain,
		}
	}
	defer resp.Body.Close()

	var title string
	contentType := resp.Header.Get("Content-Type")

	if strings.Contains(contentType, "text/html") {
		// Read the body for HTML content
		bodyBytes, err := io.ReadAll(resp.Body)
		if err != nil {
			title = fmt.Sprintf("Error reading body: %s", err.Error())
		} else {
			title = extractTitle(string(bodyBytes))
		}
	} else if strings.Contains(contentType, "application/json") {
		// Handle JSON responses
		bodyBytes, err := io.ReadAll(resp.Body)
		if err != nil {
			title = fmt.Sprintf("Error reading JSON body: %s", err.Error())
		} else {
			title = fmt.Sprintf("JSON Response: %d characters", len(bodyBytes))
		}
	} else {
		// Handle other content types
		title = fmt.Sprintf("Non-HTML content: %s", contentType)
	}

	return Result{
		URL:       urlStr,
		Title:     title,
		Status:    resp.StatusCode,
		TimeTaken: time.Since(startTime).Seconds(),
		Domain:    domain,
	}
}

// Load URLs from a file
func loadURLs(filePath string) ([]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var urls []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		url := strings.TrimSpace(scanner.Text())
		if url != "" {
			urls = append(urls, url)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return urls, nil
}

// Save results to a JSON file
func saveResults(results CombinedResults, filePath string) error {
	file, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	return encoder.Encode(results)
}

func main() {
	// Parse command line arguments
	maxWorkers := flag.Int("workers", 10, "Maximum number of concurrent workers")
	flag.Parse()

	// Get directory of the executable
	execDir, err := os.Executable()
	if err != nil {
		fmt.Printf("Error getting executable path: %s\n", err)
		os.Exit(1)
	}

	// Get the parent directory of go-crawler
	currentDir := filepath.Dir(execDir)
	parentDir := filepath.Dir(currentDir)

	// Construct path to urls.txt
	urlsFile := filepath.Join(parentDir, "urls.txt")

	// Alternative approach if the above doesn't work (for development)
	if _, err := os.Stat(urlsFile); os.IsNotExist(err) {
		// Try relative path
		urlsFile = "../urls.txt"
	}

	// Load URLs
	urls, err := loadURLs(urlsFile)
	if err != nil {
		fmt.Printf("Error loading URLs: %s\n", err)
		os.Exit(1)
	}

	fmt.Printf("Loaded %d URLs\n", len(urls))
	fmt.Printf("Starting crawl with max workers: %d\n", *maxWorkers)

	// Setup HTTP client with timeout
	client := &http.Client{
		Timeout: 10 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns:        100,
			MaxIdleConnsPerHost: 10,
			IdleConnTimeout:     30 * time.Second,
		},
	}

	// Create channels for jobs and results
	jobs := make(chan string, len(urls))
	results := make(chan Result, len(urls))

	// Start timer
	startTime := time.Now()

	// Start workers
	var wg sync.WaitGroup
	for w := 1; w <= *maxWorkers; w++ {
		wg.Add(1)
		go worker(w, jobs, results, &wg, client)
	}

	// Send jobs
	for _, url := range urls {
		jobs <- url
	}
	close(jobs)

	// Wait for all workers to finish in a separate goroutine
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect results
	var resultsList []Result
	for result := range results {
		resultsList = append(resultsList, result)
	}

	// Calculate total time
	totalTime := time.Since(startTime).Seconds()

	// Create summary
	successfulFetches := 0
	failedFetches := 0

	for _, result := range resultsList {
		if result.Status == 200 {
			successfulFetches++
		} else {
			failedFetches++
		}
	}

	summary := Summary{
		TotalURLs:         len(urls),
		SuccessfulFetches: successfulFetches,
		FailedFetches:     failedFetches,
		TotalTime:         totalTime,
		AverageTimePerURL: totalTime / float64(len(urls)),
	}

	// Print summary
	fmt.Printf("\nCrawl Summary:\n")
	fmt.Printf("Total URLs processed: %d\n", summary.TotalURLs)
	fmt.Printf("Successful fetches: %d\n", summary.SuccessfulFetches)
	fmt.Printf("Failed fetches: %d\n", summary.FailedFetches)
	fmt.Printf("Total time: %.2f seconds\n", summary.TotalTime)
	fmt.Printf("Average time per URL: %.4f seconds\n", summary.AverageTimePerURL)

	// Save results
	combinedResults := CombinedResults{
		Summary: summary,
		Results: resultsList,
	}

	resultsFile := filepath.Join(currentDir, "go_results.json")
	err = saveResults(combinedResults, resultsFile)
	if err != nil {
		fmt.Printf("Error saving results: %s\n", err)
		os.Exit(1)
	}

	fmt.Printf("Results saved to %s\n", resultsFile)
}
