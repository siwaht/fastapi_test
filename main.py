from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
llm = ChatOpenAI(model="gpt-4o-mini")

@app.post("/chat")
def chat(message: str):
    response = llm.invoke(message)
    return {"response": response.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
llm = ChatOpenAI(model="gpt-4o-mini")

@app.post("/chat")
def chat(message: str):
    response = llm.invoke(message)
    return {"response": response.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)