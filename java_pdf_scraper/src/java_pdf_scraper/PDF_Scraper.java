package java_pdf_scraper;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.client.methods.CloseableHttpResponse;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class PDF_Scraper {
    private static final int THREAD_COUNT = 20;  // Number of threads for concurrent downloading
    private static final int MAX_RETRIES = 3;  // Max retry attempts for failed requests
    private static final int TIMEOUT = 60000;  // Timeout duration in milliseconds
    private static final String BASE_URL = "https://papers.nips.cc";  // Base URL of NeurIPS papers
    private static final String OUTPUT_DIR = "D:/pdf_scraper/";  // Directory to store downloaded PDFs

    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);

        try {
            log("Connecting to main page: " + BASE_URL);
            Document document = Jsoup.connect(BASE_URL).timeout(TIMEOUT).get();
            log("Successfully connected to main page.");

            // Select paper archive links from different formats (new & old)
            Elements yearLinks = document.select("a[href^=/paper_files/paper/], a[href^=/book/]");
            log("Found " + yearLinks.size() + " paper archive links.");

            // Process each year link (archive page)
            for (Element yearLink : yearLinks) {
                String yearUrl = yearLink.absUrl("href");
                log("Processing paper archive: " + yearUrl);
                processYear(yearUrl, executor);
            }

            // Shutdown executor after submitting all tasks
            executor.shutdown();
            executor.awaitTermination(10, TimeUnit.MINUTES);
        } catch (IOException | InterruptedException e) {
            errorHandler("Main process failed", e);
        }
    }

    /**
     * Fetches all paper links from a given year’s paper archive page.
     * @param yearUrl URL of the NeurIPS paper archive page
     * @param executor Thread pool executor to handle concurrent processing
     */
    private static void processYear(String yearUrl, ExecutorService executor) {
        try {
            Document yearPage = Jsoup.connect(yearUrl)
                    .followRedirects(true)  // Ensures old URLs are handled correctly
                    .timeout(TIMEOUT)
                    .get();

            // Select paper links from various site versions (multiple patterns)
            Elements paperLinks = yearPage.select(
                "ul.paper-list li a[href$=Abstract.html], " +
                "ul.paper-list li a[href$=Abstract-Conference.html], " +
                "div.book ul.links li a[href$=.pdf], " +
                "div.main div.accordion a[href$=.pdf]"
            );

            log("Found " + paperLinks.size() + " paper links in year: " + yearUrl);

            // Process each paper link concurrently
            for (Element paperLink : paperLinks) {
                String paperHref = paperLink.absUrl("href");
                executor.submit(() -> processPaper(paperHref));
            }
        } catch (IOException e) {
            errorHandler("Failed to process year: " + yearUrl, e);
        }
    }

    /**
     * Processes a single research paper page to extract and download the PDF.
     * Retries up to MAX_RETRIES in case of failure.
     * @param paperUrl URL of the individual research paper page
     */
    private static void processPaper(String paperUrl) {
        String threadId = Thread.currentThread().getName();

        for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                log(threadId + " - Processing paper: " + paperUrl + " (Attempt " + attempt + ")");
                Document paperPage = Jsoup.connect(paperUrl).timeout(TIMEOUT).get();

                // Select the PDF link using multiple formats (covers different versions)
                Element pdfLink = paperPage.selectFirst(
                    "a[href$=Paper.pdf], " +
                    "a[href$=Paper-Conference.pdf], " +
                    "a:contains(Paper PDF), " +
                    "a:contains(Full Text)"
                );

                // If no valid PDF link is found, skip this paper
                if (pdfLink == null) {
                    log(threadId + " - No PDF link found for: " + paperUrl);
                    return;
                }

                // Extract absolute PDF URL and initiate download
                String pdfUrl = pdfLink.absUrl("href");
                log(threadId + " - Found PDF link: " + pdfUrl);
                downloadPDF(pdfUrl, sanitizeFilename(paperPage.title()));
                return;  // Exit after successful download
            } catch (IOException e) {
                if (attempt == MAX_RETRIES) {
                    errorHandler(threadId + " - Failed to process paper after " + MAX_RETRIES + " attempts: " + paperUrl, e);
                }
            }
        }
    }

    /**
     * Downloads a PDF file from the given URL and saves it with a sanitized filename.
     * @param pdfUrl URL of the research paper PDF
     * @param fileName Name of the file to be saved
     * @throws IOException If any IO error occurs during download
     */
    private static void downloadPDF(String pdfUrl, String fileName) throws IOException {
        // Ensure the filename is not too long (OS limitation)
        String safeFileName = fileName.substring(0, Math.min(fileName.length(), 200));  
        String filePath = OUTPUT_DIR + safeFileName + ".pdf";

        // Ensure output directory exists
        Files.createDirectories(Paths.get(OUTPUT_DIR));

        // Download the PDF using Apache HttpClient
        try (CloseableHttpClient httpClient = HttpClients.createDefault();
             CloseableHttpResponse response = httpClient.execute(new HttpGet(pdfUrl));
             InputStream inputStream = response.getEntity().getContent();
             FileOutputStream outputStream = new FileOutputStream(filePath)) {

            byte[] buffer = new byte[8192];  // Buffer for efficient file writing
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }
            log("Saved PDF: " + filePath);
        }
    }

    /**
     * Cleans up file names by replacing special characters to prevent file system errors.
     * @param filename Original file name
     * @return Sanitized file name
     */
    private static String sanitizeFilename(String filename) {
        return filename.replaceAll("[^\\w\\s-]", "_")  // Replace special characters with '_'
                      .replaceAll("_{2,}", "_")  // Avoid multiple underscores
                      .trim();
    }

    /**
     * Logs messages to the console in a synchronized manner.
     * @param message Log message
     */
    private static synchronized void log(String message) {
        System.out.println(message);
    }

    /**
     * Handles errors by logging the message and printing stack trace.
     * @param message Error message
     * @param e Exception object
     */
    private static synchronized void errorHandler(String message, Exception e) {
        System.err.println(message);
        e.printStackTrace();
    }
}
