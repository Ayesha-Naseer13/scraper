# NeurIPS Paper Scraper-JAVA

This project provides a Java-based web scraper that downloads research papers (PDFs) from [NeurIPS Papers](https://papers.nips.cc). The script efficiently extracts and downloads PDFs using multi-threading.

## Prerequisites
Ensure you have the following installed:
- **Java 8+** (Tested with Java 11)
- **Maven** (Optional for dependency management)
- **Internet connection** to access the website

## Setup
1. Clone or download this repository.
2. Navigate to the project folder.
3. Update the output directory in `PDF_Scraper.java` (or use a relative path):
   ```java
   private static final String OUTPUT_DIR = "pdf_downloads/"; // Set to your desired location
   ```
4. Ensure the specified directory exists or will be created automatically.

## How to Run
### Using Command Line
1. Compile the Java file:
   ```sh
   javac -cp .;jsoup-1.15.4.jar PDF_Scraper.java
   ```
2. Run the scraper:
   ```sh
   java -cp .;jsoup-1.15.4.jar PDF_Scraper
   ```

### Using an IDE (Eclipse/IntelliJ)
1. Open the project in your IDE.
2. Add `jsoup-1.15.4.jar` and Apache HttpClient libraries to your classpath.
3. Run `PDF_Scraper.java` as a Java application.

## Expected Output
- The program will log progress messages in the console.
- Downloaded PDFs will be saved in `pdf_downloads/` or your specified directory.

## Troubleshooting
- **No PDFs downloaded?**  
  - Check the website structure; it may have changed.  
  - Ensure the internet connection is stable.  
- **File permissions issue?**  
  - Run the script with appropriate permissions to write files.  
- **Slow downloads?**  
  - Increase the `THREAD_COUNT` in the script for parallel downloads.



Got it! Here is the `README.md` in editor mode:

```
# NeurIPS Papers Scraper-PYTHON

This project is a Python-based web scraper that extracts research papers from the NeurIPS Papers website ([https://papers.nips.cc](https://papers.nips.cc)). The scraper is designed to gather papers in PDF format by navigating through the annual archives of NeurIPS conference papers. It handles asynchronous requests, retries on failure, and ensures proper concurrency control.

## Features

- **Asynchronous Scraping**: Built with `asyncio` and `aiohttp` to scrape the site asynchronously for faster extraction.
- **Error Handling**: Implements retries with exponential backoff for handling failed requests.
- **Concurrency Control**: Limits the number of concurrent requests to avoid overloading the server using `asyncio.Semaphore`.
- **PDF Downloading**: Extracts and downloads PDF versions of research papers.
- **Output Directory**: Downloads papers to a specified directory on your local machine.
- **File Sanitization**: Ensures that filenames are sanitized and safe for the file system.

## Requirements

To run the scraper, make sure you have Python 3.7+ installed. You'll also need the following Python packages:

- `aiohttp`: For making asynchronous HTTP requests.
- `aiofiles`: For asynchronous file I/O operations.
- `beautifulsoup4`: For parsing HTML content.
- `requests`: For handling HTTP requests.

You can install the required packages using `pip`:

```bash
pip install aiohttp aiofiles beautifulsoup4 requests

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/neurips-papers-scraper.git
   cd neurips-papers-scraper
   ```

2. Set up the output directory where papers will be downloaded:
   - The output directory is configured as `D:/scraper/` in the code, but you can modify the `OUTPUT_DIR` variable in the script to your preferred path.

3. Run the script:
   ```bash
   python scraper.py
   ```

## Configuration

You can modify the following variables in the `scraper.py` script:

- `OUTPUT_DIR`: Path to the directory where PDFs will be saved.
- `THREAD_COUNT`: Number of concurrent requests to make at a time (default is 10).
- `MAX_RETRIES`: Maximum number of retries for failed requests (default is 3).
- `TIMEOUT`: Timeout duration for requests (default is 120 seconds).
- `USER_AGENT`: Custom user-agent string for making requests.

## Usage

1. The scraper will first collect all the links to papers from each year’s archive.
2. Then, it will navigate each paper’s page to find the PDF link and download it.
3. The downloaded PDFs will be saved in the specified `OUTPUT_DIR` with sanitized filenames.

## License

This project is licensed under the MIT License.

## Disclaimer

This project is for educational and research purposes only. Please ensure you are compliant with the website's terms of service before running the scraper.
```

This format is ready to be pasted directly into a markdown editor or a `README.md` file.

