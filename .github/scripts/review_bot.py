import os
import json
import requests
import google.generativeai as genai

# Load env variables and configure the Gemini API
# The client automatically picks up the GEMINI_API_KEY from the environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

github_token = os.getenv("GITHUB_TOKEN")
event_path = os.getenv("GITHUB_EVENT_PATH")

# Read GitHub event data (contains PR info)
with open(event_path, "r") as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]
repo = event["repository"]["full_name"]

print(f"🔎 Reviewing PR #{pr_number} in repo {repo}...")

# Read Java code (demo: single file App.java, you can expand later)
# This assumes the file exists in the correct path within your repo
try:
    with open("src/main/java/com/demo/App.java") as f:
        java_code = f.read()
except FileNotFoundError:
    print("⚠️ Error: 'src/main/java/com/demo/App.java' not found. Exiting.")
    exit()

# Ask Gemini for a review
# We use the 'gemini-1.5-pro' model here, which has a massive context window
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = (
    f"You are a strict senior Java developer reviewing code. "
    f"Review this Java code for:\n"
    f"1. Code quality\n"
    f"2. Naming conventions\n"
    f"3. Best practices\n"
    f"4. Possible bugs\n\n"
    f"Code:\n\n{java_code}"
)

# Use generate_content instead of the ChatCompletion API
response = model.generate_content(prompt)
review_comment = response.text

print("=== Review Suggestions ===")
print(review_comment)

# Post review as a PR comment
comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
headers = {"Authorization": f"token {github_token}"}
payload = {"body": f"🤖 **Gemini PR Bot Review:**\n\n{review_comment}"}

r = requests.post(comments_url, headers=headers, json=payload)

if r.status_code == 201:
    print("✅ Review comment posted successfully!")
else:
    print(f"⚠️ Failed to post comment: {r.status_code}, {r.text}")