import pandas as pd
import google.generativeai as genai
import concurrent.futures
import time
import json

# Load research papers dataset
data_file = "D:/scraper/papers/metadata.csv"
data_frame = pd.read_csv(data_file)

# Configure Gemini API
API_KEY = "AIzaSyBcShsp7fkAGOtC80FEPQ9VAgf2I25vNt8"
genai.configure(api_key=API_KEY)
llm_model = genai.GenerativeModel('gemini-pro')

# Define annotation categories
CATEGORIES = [
    "Deep Learning/Machine Learning",
    "Computer Vision",
    "Reinforcement Learning",
    "Natural Language Processing (NLP)",
    "Optimization Algorithms"
]

# Output file (append mode)
output_file = "D:/scraper/papers/annotated_metadata.csv"

# Create the CSV file with headers if it doesn't exist
pd.DataFrame(columns=['title', 'Category', 'Authors']).to_csv(output_file, index=False, mode='w')

# Function to classify a paper and extract authors
def annotate_paper(paper_title, retry_attempts=3, wait_time=10):
    delay = wait_time
    paper_abstract = "No abstract available"  # Abstracts are missing in the dataset

    for attempt in range(retry_attempts):
        try:
            query_prompt = f"""
            You are an AI research assistant. Your task is to classify the following research paper into one of these categories:
            {', '.join(CATEGORIES)}.

            Additionally, extract the **actual authors' names** based on research trends or common knowledge. If you cannot determine the authors, return "Unknown".

            Respond **only in JSON format**:
            {{
                "Category": "Selected Category",
                "Authors": "Author1, Author2, ..."
            }}

            Title: "{paper_title}"
            Abstract: "{paper_abstract}"
            """
            response = llm_model.generate_content(query_prompt)

            if hasattr(response, 'text') and response.text:
                extracted_data = response.text.strip()
            else:
                extracted_data = '{"Category": "Unknown", "Authors": "Unknown"}'

            # Parse JSON response
            try:
                result = json.loads(extracted_data)
                assigned_category = result.get("Category", "Unknown").strip()
                authors = result.get("Authors", "Unknown").strip()
            except json.JSONDecodeError:
                assigned_category, authors = "Unknown", "Unknown"

            # Validate category
            if assigned_category not in CATEGORIES:
                assigned_category = "Unknown"

            return assigned_category, authors

        except Exception as error:
            if "ResourceExhausted" in str(error) or "429" in str(error):
                print(f"Rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"Error annotating paper '{paper_title}': {error}")
                return "Error", "Error"

    print(f"Retry limit exceeded for '{paper_title}'.")
    return "Error", "Error"

# Verify necessary column exists
title_col = 'title'  # Use lowercase 'title' from metadata.csv
if title_col not in data_frame.columns:
    raise ValueError(f"Dataset must contain '{title_col}' column")

# Multithreading for annotation
THREADS = 5
total_records = len(data_frame)
processed_count = 0

with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as thread_executor:
    future_to_row = {
        thread_executor.submit(annotate_paper, row[title_col]): index
        for index, row in data_frame.iterrows()
    }

    for future in concurrent.futures.as_completed(future_to_row):
        row_index = future_to_row[future]
        try:
            category, authors = future.result()
            processed_count += 1
            print(f"Processed {processed_count}/{total_records} -> {category}, Authors: {authors}")

            # Save data row-by-row
            pd.DataFrame([[data_frame.at[row_index, title_col], category, authors]], columns=['title', 'Category', 'Authors']).to_csv(
                output_file, index=False, mode='a', header=False
            )

        except Exception as error:
            print(f"Error processing Paper {row_index + 1}: {error}")

print(f"Annotation complete! Data saved step-by-step to {output_file}")
