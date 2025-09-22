import os, json, requests
from openai import OpenAI

api_key = os.environ["OPENAI_API_KEY"]
github_token = os.environ["GITHUB_TOKEN"]
event_path = os.environ["GITHUB_EVENT_PATH"]

client = OpenAI(api_key=api_key)

with open(event_path, "r") as f:
    event = json.load(f)

pr = event["pull_request"]
repo = event["repository"]["full_name"]
pr_number = pr["number"]

files_url = pr["url"] + "/files"
headers = {"Authorization": f"token {github_token}"}
resp = requests.get(files_url, headers=headers)
files = resp.json()

diffs = []
for f in files:
    if f.get("patch"):
        diffs.append(f"File: {f['filename']}\n{f['patch']}")
diff_text = "\n\n".join(diffs)
if len(diff_text) > 6000:
    diff_text = diff_text[:6000] + "\n...diff truncated..."

prompt = f"""
You are a senior Java reviewer. Review the following PR changes and suggest improvements:

{diff_text}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=400
)

review = response.choices[0].message.content

comments_url = pr["comments_url"]
comment_body = {"body": f"🤖 **AI Review Bot**:\n\n{review}"}
requests.post(comments_url, headers=headers, json=comment_body)
