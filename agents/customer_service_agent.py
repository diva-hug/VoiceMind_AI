
import re
import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.gemini_service import (
    client,
    generate_customer_response,
)
from tools.order_tool import get_order



# 1. Generate a Groq response for a specific prompt
def generate_groq_response(prompt, max_tokens=250):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are VoiceMind AI, a professional "
                        "e-commerce customer support assistant. "
                        "Never invent policies or order details."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_completion_tokens=max_tokens,
        )

        answer = response.choices[0].message.content

        if answer:
            return answer.strip()

        return "Sorry, I couldn't generate a response right now."

    except Exception as error:
        print(f"Groq request failed: {type(error).__name__}: {error}")
        return (
            "I'm sorry, our AI support service is temporarily "
            "unavailable. Please try again shortly or contact "
            "human support."
        )


# 2. Detect customer intent using Groq
def detect_intent(question):
    prompt = f"""
Classify this e-commerce customer question into exactly ONE
of these intents:

ORDER_STATUS
DELIVERY_DELAY
RETURN
REFUND
CANCELLATION
PAYMENT
PRODUCT_INFO
GENERAL_FAQ
HUMAN_ESCALATION
UNKNOWN

Customer question: {question}

Return ONLY the intent name.
"""

    response = generate_groq_response(prompt, max_tokens=60)
    intent = response.strip().upper()

    valid_intents = {
        "ORDER_STATUS",
        "DELIVERY_DELAY",
        "RETURN",
        "REFUND",
        "CANCELLATION",
        "PAYMENT",
        "PRODUCT_INFO",
        "GENERAL_FAQ",
        "HUMAN_ESCALATION",
        "UNKNOWN",
    }

    if intent not in valid_intents:
        return "UNKNOWN"

    return intent


# 3. Extract order ID
def extract_order_id(question):
    match = re.search(r"\bORD\d+\b", question.upper())
    return match.group(0) if match else None


# 4. Handle customer questions
def generate_agent_response(question):
    question = question.strip()

    if not question:
        return "Please enter your question so I can help you."

    intent = detect_intent(question)

    print("\nDetected Intent:")
    print(intent)

    # Human support request
    if intent == "HUMAN_ESCALATION":
        return (
            "I understand you'd like to speak with a human support "
            "agent. Please contact our human support team for "
            "further assistance."
        )

    # Order status and delivery questions
    if intent in {"ORDER_STATUS", "DELIVERY_DELAY"}:
        order_id = extract_order_id(question)

        if not order_id:
            return (
                "I'd be happy to help check your order. "
                "Could you please provide your order ID, "
                "for example ORD123?"
            )

        order = get_order(order_id)

        print("\nOrder Tool Result:")
        print(order)

        if not order or not order.get("found"):
            return (
                f"I couldn't find an order with ID {order_id}. "
                "Please check the order ID and try again."
            )

        prompt = f"""
CUSTOMER QUESTION:
{question}

ORDER INFORMATION FROM THE ORDER TOOL:
{order}

Write a short, polite customer-support response.

Rules:
- Use only the order information provided.
- Mention the order ID: {order_id}.
- Do not invent delivery dates or order statuses.
- Do not claim an action has been completed unless the data confirms it.
- If a requested detail is missing, say so clearly.
"""

        return generate_groq_response(prompt, max_tokens=250)

    # Policy, payment, return, refund, product and FAQ questions
    # Use the existing RAG service and Knowledge documents.
    return generate_customer_response(question)


# 5. Local test
if __name__ == "__main__":
    question = "Can I return a product?"

    print("\n" + "=" * 60)
    print("VOICEMIND AI - CUSTOMER SERVICE AGENT")
    print("=" * 60)
    print("\nCustomer:")
    print(question)

    answer = generate_agent_response(question)

    print("\nAgent:")
    print(answer)
    print("\n" + "=" * 60)

