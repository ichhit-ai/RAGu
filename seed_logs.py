import requests
import time

url = "http://127.0.0.1:8000/ask"
clear_url = "http://127.0.0.1:8000/analytics"

queries = [
    # 1-18: Unique relevant questions
    "What is the AWS Customer Agreement?",
    "How can the agreement be terminated?",
    "What is the governing law of the agreement?",
    "Is there any limitation of liability?",
    "What happens to customer data after termination?",
    "How does AWS handle intellectual property?",
    "What are the payment terms?",
    "What is the definition of Service Content?",
    "Does the agreement cover AWS Free Tier?",
    "What are the rules regarding acceptable use?",
    "Who is responsible for security configurations?",
    "What are the warranties provided by AWS?",
    "What happens in case of a force majeure event?",
    "What is the definition of Confidential Information?",
    "Are there any indemnification obligations?",
    "Can I assign this agreement to another party?",
    "What are the taxes included in the fees?",
    "How does AWS define 'Service Suspension'?",
    "What is the definition of AWS Contracting Party?",
    
    # 19-24: Duplicates to simulate frequent queries
    "What is the governing law of the agreement?",
    "What happens to customer data after termination?",
    "How can the agreement be terminated?",
    "Is there any limitation of liability?",
    "What is the AWS Customer Agreement?",
    "What is the governing law of the agreement?",
    
    # 25-29: Exactly 5 irrelevant/out-of-scope queries
    "How to cook a pepperoni pizza?",
    "What is the capital of France?",
    "How to write a binary search tree in Python?",
    "Who won the 2022 FIFA World Cup?",
    "What is the distance between Earth and Moon?"
]

def run_seeding():
    print(f"starting to seed exactly {len(queries)} queries (including 5 irrelevant)...")
    i = 0
    while i < len(queries):
        query = queries[i]
        start = time.time()
        try:
            res = requests.post(url, json={"query": query}, timeout=45)
            latency = time.time() - start
            if res.status_code == 200:
                data = res.json()
                found = data.get("answer_found", False)
                ans = data.get("answer", "")
                
                if "429" in ans or "Too Many Requests" in ans or "failed to query" in ans:
                    print(f"\n⚠️ rate limit hit (429) on query {i+1}: '{query}'. resetting db and cooling down...")
                    requests.delete(clear_url)
                    time.sleep(35)
                    i = 0
                    continue
                    
                ans_snippet = ans[:50].replace('\n', ' ')
                print(f"[{i+1:02d}/{len(queries)}] query: '{query}' -> ok (found: {found}, time: {latency:.2f}s) | ans: {ans_snippet}...")
                i += 1
            else:
                print(f"[{i+1:02d}/{len(queries)}] query: '{query}' -> error {res.status_code}. retrying...")
                time.sleep(10)
        except Exception as e:
            print(f"[{i+1:02d}/{len(queries)}] query: '{query}' -> exception: {e}. retrying...")
            time.sleep(10)
            
        time.sleep(20.0)

if __name__ == "__main__":
    requests.delete(clear_url)
    run_seeding()
    print("done seeding logs!")
