import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def calculate_and_save_trump_stats(input_csv_file="trump_posts_daily.csv", output_txt_file="trump_baseline.txt", days_for_stats=30):
    """
    Reads daily Trump post counts, calculates mean and standard deviation for the most recent 'days_for_stats' interval
    of activity, and saves these statistics to a text file.
    """
    try:
        df = pd.read_csv(input_csv_file)
    except FileNotFoundError:
        print(f"Error: Input file {input_csv_file} not found.")
        return
    except Exception as e:
        print(f"Error reading {input_csv_file}: {e}")
        return

    if 'date' not in df.columns or 'post_count' not in df.columns:
        print(f"Error: Required columns ('date', 'post_count') not found in {input_csv_file}.")
        return

    if df.empty:
        print(f"Input file {input_csv_file} is empty. Cannot calculate stats.")
        mean_posts = 0
        std_dev_posts = 0
        actual_days_used = 0
        start_date_used = "N/A"
        end_date_used = "N/A"
    else:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date', ascending=False)

        # Determine the actual date range to use for stats
        # We want the most recent data points, up to 'days_for_stats' calendar days if available
        # or fewer if the data doesn't span that long.
        
        most_recent_date = df['date'].max()
        cutoff_date = most_recent_date - timedelta(days=days_for_stats -1) # -1 because it's inclusive

        # Filter data for the last 'days_for_stats' calendar days from the most recent post date
        recent_df = df[df['date'] >= cutoff_date]
        
        if recent_df.empty:
            print(f"No data found within the most recent {days_for_stats} calendar days from the last post date.")
            print(f"Using all available {df.shape[0]} days of data instead.")
            recent_df = df # Use all data if the window is empty
            if df.empty: # Should not happen if outer check passed, but for safety
                 mean_posts = 0
                 std_dev_posts = 0
                 actual_days_used = 0
                 start_date_used = "N/A"
                 end_date_used = "N/A"
            else:
                mean_posts = recent_df['post_count'].mean()
                std_dev_posts = recent_df['post_count'].std(ddof=0) # Population standard deviation if specified, or sample (ddof=1)
                                                                # Task doesn't specify, ddof=0 for consistency if we treat it as the "population" of this period
                actual_days_used = recent_df.shape[0] # Number of days with posts in this period
                start_date_used = recent_df['date'].min().strftime('%Y-%m-%d')
                end_date_used = recent_df['date'].max().strftime('%Y-%m-%d')
        else:
            mean_posts = recent_df['post_count'].mean()
            std_dev_posts = recent_df['post_count'].std(ddof=0) 
            actual_days_used = recent_df.shape[0]
            start_date_used = recent_df['date'].min().strftime('%Y-%m-%d')
            end_date_used = recent_df['date'].max().strftime('%Y-%m-%d')

    # Handle cases where std_dev_posts might be NaN (e.g., if only one data point)
    if pd.isna(std_dev_posts):
        std_dev_posts = 0.0
    if pd.isna(mean_posts):
        mean_posts = 0.0

    print(f"Calculating stats for Trump posts.")
    print(f"Data considered from {start_date_used} to {end_date_used} (inclusive). ({actual_days_used} days with posts in this period)")
    print(f"Mean daily posts: {mean_posts:.2f}")
    print(f"Standard deviation of daily posts: {std_dev_posts:.2f}")

    try:
        with open(output_txt_file, 'w') as f:
            f.write(f"Mean Daily Posts (last {days_for_stats} days of activity, or all available if less): {mean_posts:.2f}\n")
            f.write(f"Std Dev Daily Posts (last {days_for_stats} days of activity, or all available if less): {std_dev_posts:.2f}\n")
            f.write(f"Data Period Used for Stats: {start_date_used} to {end_date_used}\n")
            f.write(f"Number of Days with Posts in Period: {actual_days_used}\n")
        print(f"Statistics saved to {output_txt_file}")
    except Exception as e:
        print(f"Error writing to {output_txt_file}: {e}")

if __name__ == "__main__":
    calculate_and_save_trump_stats() 