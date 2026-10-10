from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

# path 

BASE_DIR =Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "Knowledge"


# load_Embedding model 

model =SentenceTransformer("all-MiniLM-L6-v2")

#load_knowledge documents 

documents = []

for file_path in KNOWLEDGE_DIR.glob("*.txt"):

    text = file_path.read_text(encoding="utf-8")

    documents.append(
        {
            "source": file_path.name,
            "content": text,
        }
    )

print("Knowledge directory:", KNOWLEDGE_DIR)
print("Documents loaded:", len(documents))
print("Document names:", [doc["source"] for doc in documents])

# Create Embeddings

texts = [document["content"] for document in documents]

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
)
embeddings =embeddings.astype("float32")

# Creatte FAISS index 

dimension = embeddings.shape[1]

index =faiss.IndexFlatL2(dimension)

index.add(embeddings)

# retrieval function 


def retrieve(query, top_k=3):
    query_embedding =model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    distances , indices = index.search(
        query_embedding,
        min(top_k,len(documents)),
    )

    results = []

    for index_position in  indices[0]:
        document =documents[index_position]

        results.append(
            {
                "source":document["source"],
                "content":document["content"],
            }
        )
    return results

# testing 

if __name__ =="__main__":
    question = "can i return a proudct "

    results = retrieve(question)

    print("\n Retrieve Documents:\n")

    for result in results:
        print("="*70)

        print("SOURCE:",result["source"])

        print(result["content"][:500])