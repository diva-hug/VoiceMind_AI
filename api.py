from fastapi import FastAPI
from pydantic import BaseModel

from agents.customer_service_agent import generate_agent_response

# Crea the FastApi  applications

app = FastAPI(
    title="VoiceMind AI API",
    description="Backend API for VoiceMind AI customer support",
    version="1.0.0",
)

# Request Format 

class SupportRequest(BaseModel):
    question: str

# Health check

@app.get("/")
def home():

    return{
        "status":"online",
        "service":"VoiceMind AI Customer Support API"
    }

# Customer support Endpoint

@app.post("/support")
def support(request: SupportRequest):

    answer =generate_agent_response( 
        request.question
        )

    return {
        "question": request.question,
        "answer": answer,
    }