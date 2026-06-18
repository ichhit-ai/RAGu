import requests
import time

url = "http://127.0.0.1:8000/ask"

queries = [
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
    "What are the dispute resolution procedures?",
    "What is the term of this agreement?",
    "What is the governing law of the agreement?",
    "What happens to customer data after termination?",
    "How can the agreement be terminated?",
    "Is there any limitation of liability?",
    "What is the AWS Customer Agreement?",
    "What is the governing law of the agreement?",
    "How can the agreement be terminated?",
    "How to cook a pepperoni pizza?",
    "What is the capital of France?",
    "How to write a binary search tree in Python?",
    "Who won the 2022 FIFA World Cup?",
    "What is the distance between Earth and Moon?",
    "Can you write a poem about autumn?",
    "What is the weather like in New York today?",
    "How to build a paper airplane?",
    "What are the best tourist places in India?",
    "Who is the CEO of Apple?"
]

print(f"seeding {len(queries)} queries...")

for i, query in enumerate(queries, 1):
    start = time.time()
    try:
        res = requests.post(url, json={"query": query}, timeout=45)
        latency = time.time() - start
        if res.status_code == 200:
            data = res.json()
            found = data.get("answer_found", False)
            ans = data.get("answer", "")[:50].replace('\n', ' ')
            print(f"[{i:02d}] query: '{query}' -> ok (found: {found}, time: {latency:.2f}s) | ans: {ans}...")
        else:
            print(f"[{i:02d}] query: '{query}' -> error {res.status_code}")
    except Exception as e:
        print(f"[{i:02d}] query: '{query}' -> failed: {e}")
    time.sleep(0.5)

print("done seeding logs!")
