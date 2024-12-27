import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

from playwright.sync_api import sync_playwright

def get_tv_show_viewers(show, season):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f'https://en.wikipedia.org/wiki/List_of_{show}_episodes')
        tables = page.query_selector_all("table")
        # index of table below can remain as same number as season
        # due to first table on pages being non-relevant
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

# Create a dataframe to store the data
df = pd.DataFrame(columns=["Overall number", "No in Season", "Title", "Directed by", "Written by", "Original air date", "US viewers (millions)", "Season", "Show"])

# Create output folders if they don't exist
if not os.path.exists("output"):
    os.makedirs("output")
if not os.path.exists("output/dataframes"):
    os.makedirs("output/dataframes")
if not os.path.exists("output/visualisations"):
    os.makedirs("output/visualisations")

# scrape data from the TV Show "The Sopranos"
show = "The_Sopranos"
seasons = [1,2,3,4,5,6]
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

# scrape data from the TV Show "Game of Throne"
show = "Game_of_Thrones"
seasons = [1,2,3,4,5,6,7,8]
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

# scrape data from the TV Show "Breaking Bad"
show = "Breaking_Bad"
seasons = [1,2,3,4,5]
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

# Rearrange columns so that it displays neater
df = df[["Show", "Overall number", "Season", "No in Season", "Title", "Directed by", "Written by", "Original air date", "US viewers (millions)"]]

# Remove citation tags from viewers column
df["US viewers (millions)"] = df["US viewers (millions)"].str.replace(r"\[.*?\]", "", regex=True)

# Replace _ with spaces in Show column
df["Show"] = df["Show"].str.replace("_", " ")

# Convert US viewers column N/A to NaN
df["US viewers (millions)"] = df["US viewers (millions)"].replace("N/A", np.nan)

# Convert Overall Number, Season and No in Season to integers, convert US viewers column to float
df["Overall number"] = df["Overall number"].astype(int)
df["Season"] = df["Season"].astype(int)
df["No in Season"] = df["No in Season"].astype(int)
df["US viewers (millions)"] = df["US viewers (millions)"].astype(float)

# Convert Original air date to datetime
df["Original air date"] = pd.to_datetime(df["Original air date"])

#save df as csv
csv_file = "output/dataframes/tv-show-viewers.csv"
df.to_csv(csv_file, index=False)

print(f"All data has now been saved to {csv_file}")

average_viewership_byshow = df.groupby("Show")["US viewers (millions)"].mean()
average_viewership_byshow.to_csv("output/dataframes/average_viewership_byshow.csv")

average_viewership_byseason = df.groupby(["Show", "Season"])["US viewers (millions)"].mean()
average_viewership_byseason.to_csv("output/dataframes/average_viewership_byseason.csv")

max_viewership_byshow = df.groupby("Show")["US viewers (millions)"].max()
max_viewership_byshow.to_csv("output/dataframes/max_viewership_byshow.csv")

min_viewership_byshow = df.groupby("Show")["US viewers (millions)"].min()
min_viewership_byshow.to_csv("output/dataframes/min_viewership_byshow.csv")

# plot heatmap of The Sopranos viewership
sopranos = df[df['Show'] == 'The Sopranos']
sopranos = sopranos[['Season', 'No in Season', 'US viewers (millions)']]
sopranos = sopranos.pivot(index='Season', columns='No in Season', values='US viewers (millions)')
fig, ax = plt.subplots(figsize=(15, 10))
sns.heatmap(sopranos, annot=True, fmt=".1f", linewidths=.5, ax=ax, cmap='RdYlGn')
plt.title('The Sopranos Viewership - US viewers (millions)')
plt.savefig('output/visualisations/sopranos-heatmap.png')

# plot heatmap of Game of Thrones viewership
got = df[df['Show'] == 'Game of Thrones']
got = got[['Season', 'No in Season', 'US viewers (millions)']]
got = got.pivot(index='Season', columns='No in Season', values='US viewers (millions)')
fig, ax = plt.subplots(figsize=(15, 10))
sns.heatmap(got, annot=True, fmt=".1f", linewidths=.5, ax=ax, cmap='RdYlGn')
plt.title('Game of Thrones Viewership - US viewers (millions)')
plt.savefig('output/visualisations/got-heatmap.png')

# plot heatmap of Breaking Bad viewership
bb = df[df['Show'] == 'Breaking Bad']
bb = bb[['Season', 'No in Season', 'US viewers (millions)']]
bb = bb.pivot(index='Season', columns='No in Season', values='US viewers (millions)')
fig, ax = plt.subplots(figsize=(15, 10))
sns.heatmap(bb, annot=True, fmt=".1f", linewidths=.5, ax=ax, cmap='RdYlGn')
plt.title('Breaking Bad Viewership - US viewers (millions)')
plt.savefig('output/visualisations/breakingbad-heatmap.png')

#plot line chart of average viewership by season
average_viewership_byseason = pd.read_csv("output/dataframes/average_viewership_byseason.csv")
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

#TO DO: Add stacked bar chart for viewerships by show (mean, max, min)
#TO DO: Tidy up script and create functions as needed