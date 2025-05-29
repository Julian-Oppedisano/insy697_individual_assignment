import pandas as pd
from datetime import datetime, timedelta

def calculate_daily_metrics(input_csv_file="hotel_reviews_raw.csv", output_csv_file="hotel_daily_metrics.csv"):
    """
    Calculates daily new review counts and mean ratings for the last 30 days.
    """
    try:
        df = pd.read_csv(input_csv_file)
    except FileNotFoundError:
        print(f"Error: Input file {input_csv_file} not found.")
        return
    except Exception as e:
        print(f"Error reading {input_csv_file}: {e}")
        return

    if 'iso_date' not in df.columns:
        print(f"Error: 'iso_date' column not found in {input_csv_file}.")
        print("Please re-run the review fetching script to include 'iso_date'.")
        return
    
    if 'rating' not in df.columns:
        print(f"Error: 'rating' column not found in {input_csv_file}.")
        return

    # Convert iso_date to datetime objects, coercing errors to NaT
    df['iso_date'] = pd.to_datetime(df['iso_date'], errors='coerce')
    df.dropna(subset=['iso_date', 'rating'], inplace=True) # Remove rows where date or rating is invalid
    
    if df.empty:
        print(f"No valid reviews with iso_date and rating found in {input_csv_file}.")
        # Create an empty df with correct columns for hotel_daily_metrics.csv
        empty_daily_df = pd.DataFrame(columns=['date', 'new_review_count', 'mean_rating'])
        empty_daily_df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
        print(f"Created empty {output_csv_file} with correct headers.")
        return

    # Determine the date range: last 30 days from the most recent review
    most_recent_date = df['iso_date'].max().normalize() # Normalize to midnight
    thirty_days_ago = most_recent_date - timedelta(days=29) # 30 days inclusive

    print(f"Most recent review date in data: {most_recent_date.strftime('%Y-%m-%d')}")
    print(f"Calculating metrics from {thirty_days_ago.strftime('%Y-%m-%d')} to {most_recent_date.strftime('%Y-%m-%d')}")

    # Filter for the last 30 days
    df_last_30_days = df[(df['iso_date'].dt.normalize() >= thirty_days_ago) & 
                         (df['iso_date'].dt.normalize() <= most_recent_date)]

    if df_last_30_days.empty:
        print(f"No reviews found within the last 30 days ({thirty_days_ago.strftime('%Y-%m-%d')} to {most_recent_date.strftime('%Y-%m-%d')}).")
    else:
        print(f"Found {len(df_last_30_days)} reviews within the last 30 days.")

    # Extract date part for grouping
    df_last_30_days['date_only'] = df_last_30_days['iso_date'].dt.normalize()

    # Calculate daily metrics
    daily_metrics = df_last_30_days.groupby('date_only').agg(
        new_review_count=('rating', 'count'),
        mean_rating=('rating', 'mean')
    ).reset_index()

    daily_metrics.rename(columns={'date_only': 'date'}, inplace=True)
    daily_metrics['mean_rating'] = daily_metrics['mean_rating'].round(2)

    # Create a full date range for the last 30 days to ensure all days are present
    all_days_in_range = pd.date_range(start=thirty_days_ago, end=most_recent_date, freq='D')
    all_days_df = pd.DataFrame(all_days_in_range, columns=['date'])

    # Merge with calculated metrics, filling missing days
    final_daily_metrics = pd.merge(all_days_df, daily_metrics, on='date', how='left')
    final_daily_metrics['new_review_count'] = final_daily_metrics['new_review_count'].fillna(0).astype(int)
    # For mean_rating, it's okay to have NaN if no reviews, or fill with 0.0 if preferred
    final_daily_metrics['mean_rating'] = final_daily_metrics['mean_rating'].fillna(0.0) 

    final_daily_metrics['date'] = final_daily_metrics['date'].dt.strftime('%Y-%m-%d')

    try:
        final_daily_metrics.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
        print(f"Successfully saved daily metrics for {len(final_daily_metrics)} days to {output_csv_file}")
        if len(final_daily_metrics) != 30:
            print(f"Warning: Expected 30 rows for daily metrics, but got {len(final_daily_metrics)}.")
    except Exception as e:
        print(f"Error writing to {output_csv_file}: {e}")

if __name__ == "__main__":
    try:
        import pandas
        from datetime import datetime, timedelta
    except ImportError:
        print("Error: pandas library is required. Please ensure it is installed.")
        exit(1)
    calculate_daily_metrics() 