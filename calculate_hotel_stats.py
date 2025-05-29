import pandas as pd

def calculate_and_save_stats(input_csv_file="hotel_reviews_raw.csv", output_txt_file="hotel_baseline.txt"):
    """
    Reads hotel reviews from a CSV, calculates the mean rating and total review count,
    and saves these statistics to a text file.
    """
    try:
        df = pd.read_csv(input_csv_file)
    except FileNotFoundError:
        print(f"Error: Input file {input_csv_file} not found.")
        return
    except Exception as e:
        print(f"Error reading {input_csv_file}: {e}")
        return

    if 'rating' not in df.columns:
        print(f"Error: 'rating' column not found in {input_csv_file}.")
        return

    # Drop rows where 'rating' is NaN or not a number, if any, before calculating mean
    df_cleaned = df.dropna(subset=['rating'])
    try:
        # Ensure rating is numeric
        df_cleaned['rating'] = pd.to_numeric(df_cleaned['rating'], errors='coerce')
        df_cleaned = df_cleaned.dropna(subset=['rating']) # Drop NaNs again if coersion created them
    except Exception as e:
        print(f"Error converting 'rating' column to numeric: {e}")
        return


    if df_cleaned.empty:
        mean_rating = 0.0 # Or handle as an error/default
        review_count = 0
        print(f"Warning: No valid ratings found in {input_csv_file} after cleaning.")
    else:
        mean_rating = df_cleaned['rating'].mean()
        review_count = len(df_cleaned) # Count of rows with valid ratings

    # The task asks for review count, which from T11 is the number of rows in hotel_reviews_raw.csv
    # However, for calculating mean rating, we use df_cleaned. For consistency in reporting "review count"
    # alongside the mean rating that was derived from those specific reviews, we'll use len(df_cleaned).
    # If the task implies the raw count from the file (which is 200 from T11), that's also an option.
    # For now, using the count of reviews that contributed to the mean.
    
    # If the overall file count is strictly needed as one of the two numbers, irrespective of valid ratings for the mean:
    total_reviews_in_file = len(df)


    print(f"Calculated Mean Rating: {mean_rating:.2f}")
    print(f"Number of Reviews (used for mean calculation): {review_count}")
    print(f"Total Reviews in File (raw count): {total_reviews_in_file}")

    try:
        with open(output_txt_file, 'w') as f:
            f.write(f"Mean Rating: {mean_rating:.2f}\n")
            # The task asks for "review count". Based on T11, it means 200.
            # The df.shape[0] or len(df) will give this from the raw file.
            f.write(f"Review Count: {total_reviews_in_file}\n")
        print(f"Successfully saved statistics to {output_txt_file}")
    except Exception as e:
        print(f"Error writing to {output_txt_file}: {e}")

if __name__ == "__main__":
    try:
        import pandas
    except ImportError:
        print("Error: pandas library is required. Please install it in your venv.")
        print("You can typically install it using: pip install pandas")
        exit(1)
    calculate_and_save_stats() 