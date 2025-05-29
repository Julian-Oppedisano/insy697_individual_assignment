import json
import pandas as pd
from datetime import datetime, timedelta

def parse_and_count_daily_posts(input_json_file="trump_posts_raw.json", output_csv_file="trump_posts_daily.csv", days_to_include=60):
    """
    Parses raw Trump Truth Social posts from a JSON file, filters for the last 'days_to_include' days,
    counts daily post frequency, and saves to a CSV file.
    """
    try:
        with open(input_json_file, 'r') as f:
            raw_posts = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {input_json_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_json_file}. It might be empty or malformed.")
        # Check if it's an error/warning message from the previous script
        try:
            with open(input_json_file, 'r') as f_check:
                content_check = f_check.read()
                if "error" in content_check.lower() or "warning" in content_check.lower():
                    print(f"Note: {input_json_file} seems to contain an error/warning message, not post data.")
        except: pass # Ignore if this check fails
        return
    except Exception as e:
        print(f"Error reading {input_json_file}: {e}")
        return

    if not isinstance(raw_posts, list) or not raw_posts:
        print(f"No posts found in {input_json_file} or data is not in expected list format.")
        # Create an empty CSV with correct headers if no posts
        pd.DataFrame(columns=['date', 'post_count']).to_csv(output_csv_file, index=False)
        print(f"Empty {output_csv_file} created.")
        return
    
    # Check if the first item contains an error or warning key from the Apify script
    if isinstance(raw_posts[0], dict) and ("error" in raw_posts[0] or "warning" in raw_posts[0]):
        print(f"The content of {input_json_file} appears to be an error/warning message:")
        print(raw_posts[0])
        # Create an empty CSV with correct headers
        pd.DataFrame(columns=['date', 'post_count']).to_csv(output_csv_file, index=False)
        print(f"Empty {output_csv_file} created due to error/warning in input.")
        return

    processed_posts = []
    for post in raw_posts:
        if not isinstance(post, dict):
            print(f"Warning: Skipping non-dictionary item in raw_posts: {post}")
            continue
        
        # Date extraction - Apify's truth-social-scraper usually provides 'createdAt' or 'date'
        # Let's check common keys and try to parse them.
        date_str = None
        possible_date_keys = ['createdAt', 'date', 'created_at', 'timestamp', 'created']
        for key in possible_date_keys:
            if key in post and post[key]:
                date_str = post[key]
                break
        
        if not date_str:
            print(f"Warning: Could not find a recognizable date field in post: {post.get('id', 'N/A')}")
            continue

        try:
            # Attempt to parse the date string. It might be ISO format or epoch timestamp.
            if isinstance(date_str, (int, float)):
                # Assuming it might be a Unix timestamp (seconds or milliseconds)
                if date_str > 1e11: # Likely milliseconds
                    dt_object = datetime.fromtimestamp(date_str / 1000)
                else: # Likely seconds
                    dt_object = datetime.fromtimestamp(date_str)
            else:
                # Try parsing common ISO-like formats
                # Apify often uses ISO format like "2024-05-20T10:00:00.000Z"
                dt_object = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            processed_posts.append({"date": dt_object.date()}) # Keep only the date part
        except ValueError as ve:
            print(f"Warning: Could not parse date string '{date_str}' for post {post.get('id', 'N/A')}: {ve}")
        except Exception as e_date:
            print(f"Warning: Error processing date for post {post.get('id', 'N/A')}: {e_date}")

    if not processed_posts:
        print("No posts could be processed for date extraction.")
        pd.DataFrame(columns=['date', 'post_count']).to_csv(output_csv_file, index=False)
        print(f"Empty {output_csv_file} created.")
        return

    df = pd.DataFrame(processed_posts)
    df['date'] = pd.to_datetime(df['date'])

    # Filter for the last 'days_to_include' days
    cutoff_date = datetime.now().date() - timedelta(days=days_to_include)
    df = df[df['date'].dt.date >= cutoff_date]

    if df.empty:
        print(f"No posts found within the last {days_to_include} days.")
        daily_counts_df = pd.DataFrame(columns=['date', 'post_count'])
    else:
        # Group by date and count posts
        daily_counts = df.groupby(df['date'].dt.date).size()
        daily_counts_df = daily_counts.reset_index(name='post_count')
        daily_counts_df.columns = ['date', 'post_count']
        daily_counts_df = daily_counts_df.sort_values(by='date', ascending=False)

    daily_counts_df.to_csv(output_csv_file, index=False)
    print(f"Daily post counts for the last {days_to_include} days saved to {output_csv_file}")
    print(f"Total posts processed after date filtering: {df.shape[0]}")
    print(f"Number of days with posts: {daily_counts_df.shape[0]}")

if __name__ == "__main__":
    parse_and_count_daily_posts() 