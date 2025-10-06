import logging
import json
from dotenv import load_dotenv
from mem0 import MemoryClient
import time
import os

# Load environment variables (e.g., API keys)
load_dotenv()

# --- Configuration ---
USER_ID = 'Arish' 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Check for the critical LLM key
if not os.getenv("OPENAI_API_KEY"):
    logging.error("CRITICAL: OPENAI_API_KEY environment variable is NOT set.")
    logging.error("Mem0 needs an LLM key (like OPENAI_API_KEY) to extract memories from conversations.")
    
# Initialize Mem0 client globally
try:
    # Mem0 Client requires MEM0_API_KEY to be set in the .env file
    mem0 = MemoryClient() 
    logging.info("Mem0 Client initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Mem0 Client: {e}. Check MEM0_API_KEY in .env file.")
    mem0 = None

def add_memory():
    """Adds a structured conversation to Mem0's memory store."""
    if mem0 is None:
        return

    messages_formatted = [
        { "role": "user", "content": "I really like Linkin Park." },
        { "role": "assistant", "content": "That is a good choice." },
        { "role": "user", "content": "I think so too." },
        { "role": "assistant", "content": "What is your favorite song by them?" },
    ]
    logging.info(f"--- 1. Starting Memory Addition for user: {USER_ID} ---")
    
    try:
        # The .add() call sends the data, triggering background LLM extraction
        response = mem0.add(messages_formatted, user_id=USER_ID)
        logging.info(f"Memory addition request sent successfully. Response: {response}")
    except Exception as e:
        # This will catch errors related to connection or key issues
        logging.error(f"Error during mem0.add() call: {e}. Check API Keys.")

def get_memory_by_query():
    """Searches for memories relevant to the user's preferences."""
    if mem0 is None:
        return "[]"
        
    query = f"What are {USER_ID}'s preferences?"
    logging.info(f"--- 2. Searching memory with query: '{query}' ---")
    
    try:
        # We search the memory store
        results = mem0.search(query, user_id=USER_ID, limit=5)

        if results and 'results' in results and results['results']:
            memories = [
                {
                    "memory": result.get("memory"),
                    "updated_at": result.get("updated_at")
                }
                for result in results['results'] if result.get("memory")
            ]
            
            memories_str = json.dumps(memories, indent=2)
            print("\n--- Retrieved Memories SUCCESS ---")
            print(memories_str)
            print("----------------------------------\n")
            return memories_str
        else:
            print(f"\n--- Retrieved Memories FAILED ---")
            print(f"No relevant memories found in search for user: {USER_ID}. Check Dashboard/API Keys.")
            print("-----------------------------------\n")
            return "[]"
            
    except Exception as e:
        logging.error(f"Error during mem0.search() call: {e}")
        return "[]"


if __name__ == "__main__":
    # 1. Add the conversation
    add_memory()
    
    # 2. WAIT: Give the LLM time to extract the fact ("Arish likes Linkin Park") 
    # and save it to the database before the search request is sent.
    logging.warning("Waiting 10 seconds for background memory extraction to complete...")
    time.sleep(10)
    
    # 3. Search the memory
    get_memory_by_query()
