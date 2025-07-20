import os
import praw
import json
from dotenv import load_dotenv

load_dotenv()
print("Authenticating with Reddit...")
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)
print("Authentication successful.")

subreddit_list = ["gamingnews", "Games", "pcgaming", "gaming", "PS5", "XboxSeriesX", "nintendo"]
new_posts = [] # This will hold the posts from this run
post_limit_per_subreddit = 25

print(f"Starting to fetch posts from {len(subreddit_list)} subreddits...")
for sub_name in subreddit_list:
    try:
        print(f"Fetching top {post_limit_per_subreddit} posts from r/{sub_name}...")
        subreddit = reddit.subreddit(sub_name)
        for post in subreddit.hot(limit=post_limit_per_subreddit):
            new_posts.append({
                "title": post.title, "url": post.url, "score": post.score,
                "id": post.id, "subreddit": sub_name, "created_utc": post.created_utc,
                "num_comments": post.num_comments, "source": "Reddit"
            })
    except Exception as e:
        print(f"Could not fetch posts from r/{sub_name}. Error: {e}")

print("\nFinished fetching posts.")

# --- APPEND LOGIC ---
output_filename = 'reddit_data.json'
existing_posts = []
if os.path.exists(output_filename):
    try:
        with open(output_filename, 'r', encoding='utf-8') as f:
            existing_posts = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Could not read {output_filename}. A new file will be created.")

# Combine the old data with the new data
combined_posts = existing_posts + new_posts

print(f"Saving {len(combined_posts)} total posts to {output_filename}...")
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(combined_posts, f, ensure_ascii=False, indent=4)

print(f"Successfully saved data to {output_filename}.")