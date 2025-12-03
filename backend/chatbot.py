from mistralai import Mistral
import json
import os

client = Mistral(api_key="YOUR_KEY_HERE")
MODEL = "mistral-large-latest"

# ---------------------------
# Load CCNA command JSON file
# ---------------------------
with open("ccna_commands.json", "r", encoding="utf-8") as f:
    ccna_data = json.load(f)


# ---------------------------
# Simple RAG retriever
# ---------------------------
def retrieve_relevant_commands(query, top_k=5):
    query = query.lower()
    scored = []

    for item in ccna_data:
        text = f"{item['topic']} {item['command']} {item['description']}".lower()
        score = sum(q in text for q in query.split())  # simple keyword match

        if score > 0:
            scored.append((score, item))

    scored = sorted(scored, key=lambda x: x[0], reverse=True)
    return [item for _, item in scored][:top_k]


# ---------------------------
# Check if question is network related
# ---------------------------
def is_network_related(text):
    keywords = [
        "vlan", "ospf", "ip", "route", "router", "switch", "dhcp", "acl", "nat",
        "pat", "ethernet", "cisco", "interface", "network", "packet", "subnet",
        "switchport", "layer", "ipv4", "ipv6", "ping", "routing", "protocol"
    ]

    text = text.lower()
    return any(k in text for k in keywords)


print("\n🤖 CCNA RAG Chatbot Ready! Type 'exit' to quit.\n")

while True:
    user_q = input("You: ")

    if user_q.lower() in ["exit", "quit"]:
        print("Chatbot: Goodbye!")
        break

    # 1. Check if question is networking-related
    if not is_network_related(user_q):
        print("Chatbot: I can only answer networking and CCNA-related questions.")
        continue

    # 2. Retrieve matching CCNA commands
    retrieved = retrieve_relevant_commands(user_q, top_k=5)

    # If no related CCNA commands found → Internet fallback mode
    if len(retrieved) == 0:
        system_prompt = """
You are a CCNA Networking Expert.

The user's question is NOT found in your CCNA JSON database. 
Warn the user clearly:

"I cannot find this in my CCNA command database. Searching online…"

Then answer their question normally using your general networking knowledge.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_q}
        ]

        response = client.chat.complete(model=MODEL, messages=messages)
        print(f"Chatbot: {response.choices[0].message.content}\n")
        continue

    # 3. If JSON has matching commands → use RAG response
    context = "\n".join(
        [f"- {c['topic']}: {c['command']} → {c['description']}" for c in retrieved]
    )

    system_prompt = f"""
You are a strict CCNA Networking Expert.

You MUST follow these rules:

1. Only answer networking questions.
2. Only use the knowledge found in this CCNA JSON command database:
{context}
3. If the answer is not directly supported by the JSON above, say:
   "This is not in my CCNA command database. Searching online…"
   Then answer normally.
4. Never invent Cisco CLI commands. Only use commands provided in the JSON.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_q}
    ]

    response = client.chat.complete(model=MODEL, messages=messages)
    print(f"Chatbot: {response.choices[0].message.content}\n")
