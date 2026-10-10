
from pathlib import Path
import re
import math

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "Knowledge"

STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "i", "you", "my",
    "me", "to", "for", "of", "in", "on", "and", "or", "it",
    "can", "could", "would", "do", "does", "did", "what",
    "how", "when", "where", "please", "want", "know"
}


def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


documents = []

for file_path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
    content = file_path.read_text(encoding="utf-8")
    documents.append({
        "source": file_path.name,
        "content": content,
        "words": set(tokenize(file_path.stem + " " + content)),
    })

print("Knowledge directory:", KNOWLEDGE_DIR)
print("Documents loaded:", len(documents))


def retrieve(query, top_k=3):
    query_words = set(tokenize(query))

    if not query_words:
        return []

    scored_documents = []

    for document in documents:
        matches = query_words & document["words"]

        if matches:
            score = len(matches) / math.sqrt(len(document["words"]))
            scored_documents.append((score, document))

    scored_documents.sort(key=lambda item: item[0], reverse=True)

    return [
        {
            "source": document["source"],
            "content": document["content"],
        }
        for score, document in scored_documents[:top_k]
    ]


if __name__ == "__main__":
    results = retrieve("Can I return a product?")

    for result in results:
        print("\nSOURCE:", result["source"])
        print(result["content"][:500])