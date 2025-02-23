import pandas as pd
import faiss
import numpy as np
import pickle
import openai
from tqdm import tqdm
import os
from dotenv import load_dotenv
from thefuzz import process

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

file_path = "datasets/globaldataset.csv"


def search_database(query, limit=8):
    df = pd.read_csv("datasets/globaldataset.csv")
    data = df["title"].tolist()
    matches = process.extract(query, data, limit=limit)
    matched_names = [match[0] for match in matches]
    filtered_df = df[df["title"].isin(matched_names)]
    result_json = filtered_df.to_json(orient="records")
    return result_json


def load_csv(file_path):
    """Load CSV and check if 'title' column exists, while handling format errors."""
    try:
        # Load the CSV and handle bad rows
        df = pd.read_csv(file_path, dtype=str, on_bad_lines="skip")
        print("📝 CSV Columns Found:", df.columns.tolist())  # Print all column names

        # Standardize column names (strip spaces)
        df.columns = df.columns.str.strip()

        if "title" not in df.columns:
            raise ValueError(
                "🚨 The CSV file does not contain a 'title' column. Check column names!"
            )

        df = df.dropna(subset=["title"])  # Drop empty values
        return df

    except Exception as e:
        print(f"🚨 Error loading CSV: {e}")
        return None


def get_embedding(text, model="text-embedding-3-small", max_retries=3):
    """Convert text into an embedding vector using OpenAI, with retry handling."""
    text = text.strip()  # Remove extra spaces/newlines
    for attempt in range(max_retries):
        try:
            response = openai.embeddings.create(input=[text], model=model)
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            print(
                f"⚠️ OpenAI API Error on '{text}' (Attempt {attempt + 1}/{max_retries}): {e}"
            )
    print(f"Failed to generate embedding for '{text}', using zero vector.")
    return np.zeros(1536, dtype=np.float32)


def create_faiss_index(csv_path):
    """Convert each food name into a vector and store in FAISS."""
    df = load_csv(csv_path)

    # Extract the column 'title' which contains food names
    food_names = df["title"].astype(str).tolist()

    print(f"Found {len(food_names)} food items. Generating embeddings...")

    # Convert each food name to an embedding (LOOP THROUGH EACH NAME)
    embeddings_list = []

    # Use tqdm for progress bar
    for name in tqdm(food_names, desc="Generating embeddings"):
        embedding = get_embedding(name)  # Get the embedding vector
        embeddings_list.append(embedding)  # Store it in the list

    # Convert the list of embeddings into a NumPy array
    embeddings = np.array(embeddings_list, dtype=np.float32)

    # Check if embeddings are valid
    if embeddings.shape[0] == 0:
        raise ValueError("No embeddings were generated")

    # Get the embedding size (dimension)
    dimension = embeddings.shape[1]

    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)  # Add all vectors

    # Save FAISS index to a file
    faiss.write_index(index, "faiss_index.bin")

    # Save mapping of food names & other data
    with open("id_mapping.pkl", "wb") as f:
        pickle.dump(df.to_dict(orient="records"), f)

    print("FAISS index and ID mapping saved successfully!")


if __name__ == "__main__":
    print("\nRunning FAISS vectorization pipeline...\n")

    # Step 1: Create and Save FAISS Index
    create_faiss_index(file_path)

    # Step 2: Load and Display FAISS Index for Verification
    print("\nLoading FAISS index to verify data...")

    try:
        index = faiss.read_index("faiss_index.bin")
        print(f"FAISS index loaded with {index.ntotal} items.")

        # Load ID mapping
        with open("id_mapping.pkl", "rb") as f:
            id_mapping = pickle.load(f)

        # Display the first few mappings
        print("\nChecking first 5 FAISS mappings:")
        for i, item in enumerate(id_mapping[:5]):
            print(f"FAISS Index {i} -> CSV Row {i}: {item['title']}")

    except Exception as e:
        print(f"Error loading FAISS index or mapping: {e}")

    print("\nProcess completed successfully!")
