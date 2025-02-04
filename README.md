# NeurIPS Paper Scraper

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

