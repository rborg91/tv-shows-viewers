import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

df = pd.DataFrame(columns=["Overall number", "No in Season", "Title", "Directed by", "Written by", "Original air date", "US viewers (millions)", "Season", "Show"])

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

#save df as csv
csv_file = "tv-show-viewers.csv"
df.to_csv(csv_file, index=False)

print(f"All data has now been saved to {csv_file}")

# TO DO: Do some numpy calculations e.g. mean, max, min etc.
# TO DO: start creating matplotlib visualisations
