
import os

from dotenv import load_dotenv
from groq import Groq

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.retriever import retrieve

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file.")


client = Groq(
    api_key=api_key,
    timeout=20.0,
    max_retries=0
)


def generate_customer_response(question):
    try:
        results = retrieve(question, top_k=3)

        print("\nRetrieved Documents:")

        context_parts = []

        for result in results:
            print("-", result["source"])

            content = result["content"][:3000]

            context_parts.append(
                f"Source: {result['source']}\n{content}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a professional e-commerce customer support agent.

Answer the customer's question using ONLY the knowledge base
provided below.

KNOWLEDGE BASE:
{context}

CUSTOMER QUESTION:
{question}

RULES:
- Use only the provided knowledge base.
- Do not invent policies or order information.
- Do not make unsupported promises.
- If information is insufficient, clearly say so.
- Be polite and helpful.
- Keep the answer concise and direct.
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful customer support assistant. "
                        "Follow the knowledge-base restrictions."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=400
        )

        answer = response.choices[0].message.content

        if not answer:
            return "Sorry, I couldn't generate a response right now."

        return answer.strip()

    except Exception as error:
        print("\nGroq API Error:")
        print(f"{type(error).__name__}: {error}")

        return (
            "I'm sorry, I'm unable to process your request right now. "
            "Please try again later or contact human support."
        )


if __name__ == "__main__":
    question = "Can I return a product?"

    print("\n" + "=" * 60)
    print("VOICEMIND AI - CUSTOMER SUPPORT TEST")
    print("=" * 60)

    print("\nCustomer Question:")
    print(question)

    answer = generate_customer_response(question)

    print("\nGroq Response:")
    print(answer)

    print("\n" + "=" * 60)