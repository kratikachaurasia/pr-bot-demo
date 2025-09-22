import os
import json
import requests
import openai

# Load env variables
openai.api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
event_path = os.getenv("GITHUB_EVENT_PATH")

# Read GitHub event data (contains PR info)
with open(event_path, "r") as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]
repo = event["repository"]["full_name"]

print(f"🔎 Reviewing PR #{pr_number} in repo {repo}...")

# Read Java code (demo: single file App.java, you can expand later)
with open("src/main/java/com/demo/App.java") as f:
    java_code = f.read()

# Ask OpenAI for review
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a strict senior Java developer reviewing code."},
        {"role": "user", "content": f"Review this Java code for:\n1. Code quality\n2. Naming conventions\n3. Best practices\n4. Possible bugs\n\nCode:\n\n{java_code}"}
    ]
)

review_comment = response.choices[0].message["content"]

print("=== Review Suggestions ===")
print(review_comment)

# Post review as a PR comment
comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
headers = {"Authorization": f"token {github_token}"}
payload = {"body": f"🤖 **PR Bot Review:**\n\n{review_comment}"}

r = requests.post(comments_url, headers=headers, json=payload)

if r.status_code == 201:
    print("✅ Review comment posted successfully!")
else:
    print(f"⚠️ Failed to post comment: {r.status_code}, {r.text}")
