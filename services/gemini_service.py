import os

from dotenv import load_dotenv
from google import genai

from rag.retriever import retrieve


# 1.Load environment variables

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

# 2. Create Gemini client

client = genai.Client(
    api_key=api_key
)


# 3. Generate customer support response

def generate_customer_response(question):

    # Retrieve relevant documents from Knowledge Base

    results = retrieve(
        question,
        top_k=3
    )

    print("\nRetrieved Documents:")

    for result in results:
        print("-", result["source"])


    # Build a smaller RAG context

    context_parts = []

    for result in results:

        content = result["content"]

        # Keep the context manageable
        content = content[:3000]

        context_parts.append(
            f"Source: {result['source']}\n"
            f"{content}"
        )

    context = "\n\n".join(context_parts)


    # Create prompt for Gemini

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
- Do not invent policies or information.
- Do not invent order information.
- Do not make promises that are not supported by the knowledge base.
- If the information is insufficient, clearly say that you do not have enough information.
- Be polite and helpful.
- Keep the answer concise.
- Give the customer a clear and direct answer.
"""

    # Generate response using Gemini

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        if not response.text:
            return "I'm sorry, but I couldn't generate a response right now."

        return response.text.strip()

    except Exception as error:

        print("\nGemini API Error:")
        print(error)

        return (
            "I'm sorry, I'm unable to process your request right now. "
            "Please try again later or contact human support."
        )

# 4. Test the complete RAG + Gemini pipeline

if __name__ == "__main__":

    question = "Can I return a product?"

    print("\n" + "=" * 60)
    print("VOICE MIND AI - CUSTOMER SUPPORT TEST")
    print("=" * 60)

    print("\nCustomer Question:")
    print(question)

    answer = generate_customer_response(question)

    print("\nGemini Response:")
    print(answer)

    print("\n" + "=" * 60)