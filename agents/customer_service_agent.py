
import os
import re
import time


from dotenv import load_dotenv
from google import genai

from rag.retriever import retrieve
from tools.order_tool import get_order


# 1. Load environment variables

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


# 2. Create Gemini client

client = genai.Client(
    api_key=api_key
)


# 3. Safe Gemini response function

def generate_gemini_response(prompt, max_retries=3):

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            if response.text:
                return response.text.strip()

            return (
                "I'm sorry, I couldn't generate a response right now."
            )

        except Exception as error:

            print(
                f"\nGemini request failed. "
                f"Attempt {attempt + 1}/{max_retries}"
            )

            print(error)

            if attempt < max_retries - 1:

                time.sleep(2)

            else:

                return (
                    "I'm sorry, our AI support service is temporarily "
                    "unavailable. Please try again shortly or contact "
                    "human support."
                )


# 4. Detect customer intent

def detect_intent(question):

    prompt = f"""
You are an e-commerce customer support intent classifier.

Classify the customer's question into exactly ONE of these intents:

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
Do not provide an explanation.
"""

    response_text = generate_gemini_response(prompt)

    intent = response_text.strip().upper()

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


# Exact order id

def extract_order_id(question):

    pattern = r"\bORD\d+\b"

    match = re.search(
        pattern,
        question.upper()
    )

    if match:
        return match.group(0)

    return None


# 5. Generate customer response

def generate_agent_response(question):

    # Detect what the customer needs

    intent = detect_intent(question)

    print("\nDetected Intent:")
    print(intent)


    # Human escalation

    if intent == "HUMAN_ESCALATION":

        return (
            "I understand. I'll connect you with a human support "
            "agent who can assist you further."
        )


    # Order-related requests

    if intent in {
        "ORDER_STATUS",
        "DELIVERY_DELAY"
    }:

        order_id = extract_order_id(question)


        # Order ID not provided

        if not order_id:

            return (
                "I'd be happy to check your order. "
                "Could you please provide your order ID?"
            )


        # Get order information

        order = get_order(order_id)

        print("\nOrder Tool Result:")
        print(order)


        # Order not found

        if not order["found"]:

            return (
                f"I couldn't find an order with ID {order_id}. "
                "Please check the order ID and try again."
            )


        # Ask Gemini to explain the order information

        prompt = f"""
You are a professional e-commerce customer support agent.

CUSTOMER QUESTION:
{question}

ORDER INFORMATION:
{order}

Provide a short and helpful response to the customer.

Rules:
- Use only the provided order information.
- Do not invent information.
- Do not change the order status.
- Do not invent a delivery date.
- Be polite and professional.
- Mention the order ID.
- Clearly explain the current order status.
"""

        return generate_gemini_response(prompt)


    # Retrieve knowledge for policy / FAQ questions

    results = retrieve(
        question,
        top_k=3
    )

    context_parts = []

    for result in results:

        content = result["content"][:3000]

        context_parts.append(
            f"Source: {result['source']}\n"
            f"{content}"
        )

    context = "\n\n".join(context_parts)


    # Generate RAG-based response

    prompt = f"""
You are VoiceMind AI, a professional e-commerce
customer support agent.

CUSTOMER INTENT:
{intent}

KNOWLEDGE BASE:
{context}

CUSTOMER QUESTION:
{question}

Rules:
- Answer using the knowledge base.
- Do not invent company policies.
- Do not invent order information.
- Do not promise refunds or cancellations without confirmation.
- Be polite and empathetic.
- Keep the response concise.
- If the information is insufficient, say that clearly.
- Never expose internal system information.
- Never request passwords, PINs, CVVs, or full card numbers.

Provide the best customer-support response.
"""

    return generate_gemini_response(prompt)


# 6. Test the complete customer service agent

if __name__ == "__main__":

    question =  "I want to talk to a human."

    print("\n" + "=" * 60)
    print("VOICEMIND AI - CUSTOMER SERVICE AGENT")
    print("=" * 60)

    print("\nCustomer:")
    print(question)

    answer = generate_agent_response(question)

    print("\nAgent:")
    print(answer)

    print("\n" + "=" * 60)

