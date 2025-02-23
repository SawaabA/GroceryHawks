from text_classification import *

# text = "Hotdog"
# value = get_embedding(text)
# print(value)

import faiss
import numpy as np
import pickle

# Load FAISS index
faiss_index_path = "faiss_index.bin"
index = faiss.read_index(faiss_index_path)

# Load the ID mapping
id_mapping_path = "id_mapping.pkl"
with open(id_mapping_path, "rb") as f:
    id_mapping = pickle.load(f)

# Function to print full vector for a given index
def print_full_vector(index_id):
    vector = np.zeros((index.d,), dtype=np.float32)
    index.reconstruct(index_id, vector)
    
    print(f"\nFAISS Index {index_id} -> Food: {id_mapping[index_id]['title']}")
    print(f"Full Vector:\n{vector}")

# Print full vectors for the first 3 food items
for i in range(3):
    print_full_vector(i)