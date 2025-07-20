import os
import praw
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("Authenticating with Reddit...")
# Authenticate with Reddit using credentials from .env
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)
print("Authentication successful.")

# List of gaming-related subreddits to scrape
subreddit_list = [
    "gamingnews",
    "Games",
    "pcgaming",
    "gaming",
    "PS5",
    "XboxSeriesX",
    "nintendo"
]

# A list to hold all the posts we gather
all_posts = []
post_limit_per_subreddit = 25 # You can adjust this number

print(f"Starting to fetch posts from {len(subreddit_list)} subreddits...")

# Loop through each subreddit in our list
for sub_name in subreddit_list:
    try:
        print(f"Fetching top {post_limit_per_subreddit} posts from r/{sub_name}...")
        subreddit = reddit.subreddit(sub_name)
        
        # Fetch the 'hot' posts from the subreddit
        for post in subreddit.hot(limit=post_limit_per_subreddit):
            # Append the data for each post to our list
            all_posts.append({
                "title": post.title,
                "url": post.url,
                "score": post.score,
                "id": post.id,
                "subreddit": sub_name, # Track which subreddit it came from
                "created_utc": post.created_utc,
                "num_comments": post.num_comments,
                "source": "Reddit"
            })
    except Exception as e:
        print(f"Could not fetch posts from r/{sub_name}. Error: {e}")

print("\nFinished fetching posts.")

# Define the output filename
output_filename = 'reddit_data.json'

# Save the collected data to a JSON file
print(f"Saving {len(all_posts)} posts to {output_filename}...")
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=4)

print(f"Successfully saved data to {output_filename}.")