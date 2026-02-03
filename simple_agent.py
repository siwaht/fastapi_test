"""
Simple LangChain AI Agent Example
Run this file directly to test the agent without FastAPI
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

# Define tools
@tool
def get_weather(location: str) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is sunny and 72°F"

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create the agent
tools = [get_weather, calculate]
agent_executor = create_react_agent(llm, tools)

# Test the agent
if __name__ == "__main__":
    print("LangChain Agent Test")
    print("=" * 50)
    
    # Example queries
    queries = [
        "What's the weather in New York?",
        "Calculate 45 + 67",
        "What's the weather in Paris and what is 100 * 2?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        result = agent_executor.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        response = result.get("messages", [])[-1].content
        print(f"Response: {response}")
