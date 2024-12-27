import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns
from playwright.sync_api import sync_playwright

def get_tv_show_viewers(show, season):
    """
    Fetches the list of viewers for each episode of a given TV show and season from Wikipedia.

    Args:
        show (str): The name of the TV show.
        season (int): The season number of the TV show.

    Returns:
        list: A list of lists, where each inner list contains data for an episode, including:
            - Episode details (e.g., title, air date, etc.)
            - Season number
            - Show name
            - US viewership (in millions)

    Raises:
        Exception: If there is an issue with fetching or parsing the data from Wikipedia.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f'https://en.wikipedia.org/wiki/List_of_{show}_episodes')
        tables = page.query_selector_all("table")
        season_table = tables[season]
        rows = season_table.query_selector_all("tr")
        results = []

        for row in rows:
            cells = row.query_selector_all("th, td")
            row_data = [cell.inner_text().strip() for cell in cells if cell.inner_text().strip()]
            if row_data:
                row_data.append(season)
                row_data.append(show)
                results.append(row_data)

        browser.close()
    return results

def create_output_folders():
    """
    Creates the necessary output folders if they do not already exist.

    This function checks for the existence of the "output" directory and its
    subdirectories "output/dataframes" and "output/visualisations". If any of
    these directories do not exist, they are created.
    """
    if not os.path.exists("output"):
        os.makedirs("output")
    if not os.path.exists("output/dataframes"):
        os.makedirs("output/dataframes")
    if not os.path.exists("output/visualisations"):
        os.makedirs("output/visualisations")

def scrape_show_data(show, seasons):
    """
    Scrapes TV show data for the specified show and seasons.

    This function retrieves data for each season of the given TV show and compiles it into a single DataFrame.
    It handles any exceptions that occur during the data retrieval process and continues with the next season.

    Parameters:
    show (str): The name of the TV show.
    seasons (list): A list of season numbers to scrape data for.

    Returns:
    pd.DataFrame: A DataFrame containing the scraped data with columns:
        - "Overall number"
        - "No in Season"
        - "Title"
        - "Directed by"
        - "Written by"
        - "Original air date"
        - "US viewers (millions)"
        - "Season"
        - "Show"
    """
    df = pd.DataFrame(columns=["Overall number", "No in Season", "Title", "Directed by", "Written by", "Original air date", "US viewers (millions)", "Season", "Show"])
    for season in seasons:
        try:
            print(f"Getting data for {show} Season {season}")
            results = get_tv_show_viewers(show, season)
            df1 = pd.DataFrame(results[1:], columns=["Overall number", "No in Season", "Title", "Directed by", "Written by", "Original air date", "US viewers (millions)", "Season", "Show"])
            df = pd.concat([df, df1])
            df = df[df["Original air date"].notna()]
        except Exception as e:
            print(f"An error occurred while processing {show} season {season}: {e}")
            continue
    return df

def clean_and_save_data(df):
    """
    Cleans the input DataFrame and saves it to a CSV file.

    This function performs the following operations:
    1. Selects specific columns from the DataFrame.
    2. Removes any text within square brackets from the "US viewers (millions)" column.
    3. Replaces underscores with spaces in the "Show" column.
    4. Replaces "N/A" values in the "US viewers (millions)" column with NaN.
    5. Converts the "Overall number", "Season", and "No in Season" columns to integers.
    6. Converts the "US viewers (millions)" column to float.
    7. Converts the "Original air date" column to datetime.
    8. Saves the cleaned DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The input DataFrame containing TV show data.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    df = df[["Show", "Overall number", "Season", "No in Season", "Title", "Directed by", "Written by", "Original air date", "US viewers (millions)"]]
    df["US viewers (millions)"] = df["US viewers (millions)"].str.replace(r"\[.*?\]", "", regex=True)
    df["Show"] = df["Show"].str.replace("_", " ")
    df["US viewers (millions)"] = df["US viewers (millions)"].replace("N/A", np.nan)
    df["Overall number"] = df["Overall number"].astype(int)
    df["Season"] = df["Season"].astype(int)
    df["No in Season"] = df["No in Season"].astype(int)
    df["US viewers (millions)"] = df["US viewers (millions)"].astype(float)
    df["Original air date"] = pd.to_datetime(df["Original air date"])
    csv_file = "output/dataframes/tv-show-viewers.csv"
    df.to_csv(csv_file, index=False)
    print(f"All data has now been saved to {csv_file}")
    return df

def save_aggregated_data(df):
    """
    Aggregates viewership data by show and season, and saves the results to CSV files.

    Parameters:
    df (pandas.DataFrame): DataFrame containing TV show viewership data with columns "Show", "Season", and "US viewers (millions)".

    The function performs the following aggregations and saves the results to CSV files:
    - Average viewership by show: saved to "output/dataframes/average-viewership-byshow.csv"
    - Average viewership by show and season: saved to "output/dataframes/average-viewership-byseason.csv"
    - Maximum viewership by show: saved to "output/dataframes/max-viewership-byshow.csv"
    - Minimum viewership by show: saved to "output/dataframes/min-viewership-byshow.csv"
    """
    average_viewership_byshow = df.groupby("Show")["US viewers (millions)"].mean()
    average_viewership_byshow.to_csv("output/dataframes/average-viewership-byshow.csv")

    average_viewership_byseason = df.groupby(["Show", "Season"])["US viewers (millions)"].mean()
    average_viewership_byseason.to_csv("output/dataframes/average-viewership-byseason.csv")

    max_viewership_byshow = df.groupby("Show")["US viewers (millions)"].max()
    max_viewership_byshow.to_csv("output/dataframes/max-viewership-byshow.csv")

    min_viewership_byshow = df.groupby("Show")["US viewers (millions)"].min()
    min_viewership_byshow.to_csv("output/dataframes/min-viewership-byshow.csv")

def plot_heatmap(df, show):
    """
    Plots a heatmap of US viewership for a given TV show.

    Parameters:
    df (pandas.DataFrame): DataFrame containing the TV show data with columns 'Show', 'Season', 'No in Season', and 'US viewers (millions)'.
    show (str): The name of the TV show to plot the heatmap for.

    The function saves the heatmap as a PNG file in the 'output/visualisations/' directory.
    """
    show_df = df[df['Show'] == show]
    show_df = show_df[['Season', 'No in Season', 'US viewers (millions)']]
    show_df = show_df.pivot(index='Season', columns='No in Season', values='US viewers (millions)')
    fig, ax = plt.subplots(figsize=(15, 10))
    sns.heatmap(show_df, annot=True, fmt=".1f", linewidths=.5, ax=ax, cmap='RdYlGn', cbar=False)
    plt.title(f'{show} Viewership - US viewers (millions)')
    plt.savefig(f'output/visualisations/{show.lower().replace(" ", "")}-heatmap.png')

def plot_line_chart():
    """
    Reads average viewership data from a CSV file and plots a line chart.

    The function reads data from 'output/dataframes/average-viewership-byseason.csv',
    creates a line plot showing the average viewership by season for different TV shows,
    and saves the plot as 'output/visualisations/average-viewership-byseason.png'.

    The plot includes:
    - X-axis: Season
    - Y-axis: Average US viewership in millions
    - Line color: Different TV shows
    """
    average_viewership_byseason = pd.read_csv("output/dataframes/average-viewership-byseason.csv")
    fig, ax = plt.subplots(figsize=(15, 10))
    sns.lineplot(data=average_viewership_byseason, x='Season', y='US viewers (millions)', hue='Show', ax=ax)
    plt.title('Average Viewership by Season', fontsize=14)
    plt.xlabel('Season', fontsize=16)
    plt.ylabel('Average Viewership (millions)', fontsize=16)
    plt.setp(ax.lines, linewidth=5)
    plt.legend(fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.savefig('output/visualisations/average-viewership-byseason.png')

def plot_stacked_bar_chart():
    """
    Reads viewership data from CSV files and plots a stacked bar chart showing
    the maximum, average, and minimum viewership for each TV show.

    The function performs the following steps:
    1. Reads the average, maximum, and minimum viewership data from CSV files.
    2. Creates a bar chart with the viewership data.
    3. Sets the x-axis label to 'Show' and y-axis label to 'US Viewers (Millions)'.
    4. Sets the title of the plot to 'Viewership by Show'.
    5. Sets the x-axis tick labels to the names of the shows.
    6. Adds a legend to differentiate between max, average, and min viewership.
    7. Saves the plot as a PNG file in the specified output directory.

    The CSV files should be located in the 'output/dataframes/' directory and
    should have the following filenames:
    - 'average-viewership-byshow.csv'
    - 'max-viewership-byshow.csv'
    - 'min-viewership-byshow.csv'

    The resulting plot will be saved as 'average-max-min-viewership-byshow.png'
    in the 'output/visualisations/' directory.

    Note:
    - The CSV files should have a column named 'Show' containing the names of the TV shows.
    - The function uses the pandas and matplotlib libraries.
    """
    average_viewership = pd.read_csv('output/dataframes/average-viewership-byshow.csv')
    max_viewership = pd.read_csv('output/dataframes/max-viewership-byshow.csv')
    min_viewership = pd.read_csv('output/dataframes/min-viewership-byshow.csv')
    fig, ax = plt.subplots()
    max_viewership.set_index('Show').plot(kind='bar', ax=ax, color='r')
    average_viewership.set_index('Show').plot(kind='bar', ax=ax, color='b')
    min_viewership.set_index('Show').plot(kind='bar', ax=ax, color='g')
    plt.xlabel('Show', fontsize=14)
    plt.ylabel('US Viewers (Millions)', fontsize=14)
    plt.title('Viewership by Show', fontsize=16)
    ax.set_xticklabels(max_viewership['Show'], rotation=0)
    plt.legend(['Max Viewership', 'Average Viewership', 'Min Viewership'])
    plt.savefig('output/visualisations/average-max-min-viewership-byshow.png')

def main():
    create_output_folders()
    
    shows = {
        "The_Sopranos": [1, 2, 3, 4, 5, 6],
        "Game_of_Thrones": [1, 2, 3, 4, 5, 6, 7, 8],
        "Breaking_Bad": [1, 2, 3, 4, 5]
    }
    
    df = pd.DataFrame()
    for show, seasons in shows.items():
        show_data = scrape_show_data(show, seasons)
        df = pd.concat([df, show_data])
    
    df = clean_and_save_data(df)
    save_aggregated_data(df)
    
    for show in shows.keys():
        plot_heatmap(df, show.replace("_", " "))
    
    plot_line_chart()
    plot_stacked_bar_chart()

    print("All visualisations have been saved to the output/visualisations folder")

if __name__ == "__main__":
    main()

#TO DO: Tidy up visualisations and make them consistent