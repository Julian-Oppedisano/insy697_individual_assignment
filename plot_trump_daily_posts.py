import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_daily_trump_posts(input_csv_file="trump_posts_daily.csv", output_plot_file="trump_daily_posts_plot.png"):
    """
    Reads daily Trump post counts and generates a line plot of posts over time.
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
        print(f"Input file {input_csv_file} is empty. Cannot generate plot.")
        # Optionally, create a blank plot or just return
        plt.figure(figsize=(10, 5))
        plt.title('Daily Trump Posts (No Data)')
        plt.xlabel('Date')
        plt.ylabel('Number of Posts')
        plt.text(0.5, 0.5, 'No data available to plot.', ha='center', va='center', transform=plt.gca().transAxes)
        try:
            plt.savefig(output_plot_file)
            print(f"Empty plot saved to {output_plot_file} as no data was available.")
        except Exception as e_save:
            print(f"Error saving empty plot to {output_plot_file}: {e_save}")
        return

    try:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')

        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], df['post_count'], marker='o', linestyle='-', color='b')
        
        plt.title('Daily Truth Social Post Counts for Donald Trump (Last 60 Days of Activity)')
        plt.xlabel('Date')
        plt.ylabel('Number of Posts')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.xticks(rotation=45)
        
        # Format x-axis to show dates more clearly
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=15))
        plt.tight_layout() # Adjust layout to prevent labels from overlapping

        plt.savefig(output_plot_file)
        print(f"Plot of daily Trump post counts saved to {output_plot_file}")
        print("Plotting completed successfully.")

    except Exception as e_plot:
        print(f"An error occurred during plotting: {e_plot}")

if __name__ == "__main__":
    # Ensure Matplotlib uses a non-interactive backend if running in an environment without a display server
    # This is generally good practice for scripts that save plots to files.
    try:
        current_backend = plt.get_backend()
        # print(f"Matplotlib backend: {current_backend}") # Optional: check current backend
        # If the backend is interactive (e.g., TkAgg, QtAgg) and might cause issues in a headless environment,
        # you could switch it. For saving to file, 'Agg' is often a safe choice.
        if not plt.isinteractive() and current_backend.lower() not in ['agg', 'cairo', 'svg', 'pdf', 'ps']:
            plt.switch_backend('Agg')
            # print(f"Switched Matplotlib backend to: {plt.get_backend()}")
    except Exception as e_backend:
        print(f"Note: Could not switch Matplotlib backend if needed: {e_backend}")
        
    plot_daily_trump_posts() 