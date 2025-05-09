"""
Find the median for each statistic. Calculate the mean and standard deviation for each
statistic across all players and for each team.
"""
import pandas as pd
import numpy as np

file_path = r'C:\Users\Hungdever\Desktop\My_study\EPL\data\results.csv'
output_path = r'C:\Users\Hungdever\Desktop\My_study\EPL\data\results2.csv'

try:
    df = pd.read_csv(file_path)
    print(f"Successfully read data from {file_path}")
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit() 
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit() 

# Identify numeric statistic columns 
stat_cols_original = [] 
all_player_column_names = ['Teams_or_players'] 
all_player_stats_values = ['All']        

for col in df.columns:
    if col in ['player', 'team', 'Req_Nation', 'Req_Position']:
        continue

    numeric_series = pd.to_numeric(df[col], errors='coerce')

    if numeric_series.notna().any():
        stat_cols_original.append(col)

        median_val = numeric_series.median()
        mean_val = numeric_series.mean()
        std_val = numeric_series.std()

        base_col_name = col.replace('%', 'Pct').replace('/', 'Per')
        median_name = f"Median_{base_col_name}"
        mean_name = f"Mean_{base_col_name}"
        std_name = f"Std_{base_col_name}"

        all_player_column_names.extend([median_name, mean_name, std_name])
        all_player_stats_values.extend([median_val, mean_val, std_val])


# Create 'All' Players Stats Row 
if len(stat_cols_original) > 0:
    result_df = pd.DataFrame([all_player_stats_values], columns=all_player_column_names)
    print("\nStatistics for 'All' Players:")

else:
    print("\nNo numeric statistic columns found. Cannot proceed.")
    exit() 

# Calculate Stats for Each Team 
team_stats_list = [] 
team_names_list = sorted(list(df['team'].unique())) 

print("\nCalculating Statistics for Each Team")
for team_name in team_names_list:
    teamdf = df[df['team'] == team_name].copy() 
    if teamdf.empty:
        print(f"No players found for team '{team_name}', skipping.")
        continue

    print(f"Processing team: {team_name} ({len(teamdf)} players)")
    team_row_stats = [team_name] 

    for col in stat_cols_original:
        numeric_series_team = pd.to_numeric(teamdf[col], errors='coerce')

        if numeric_series_team.notna().any():
            median_val = numeric_series_team.median()
            mean_val = numeric_series_team.mean()
            std_val = numeric_series_team.std()
        else:
            median_val = np.nan
            mean_val = np.nan
            std_val = np.nan

        team_row_stats.extend([median_val, mean_val, std_val])

    team_stats_list.append(team_row_stats)

# Create Team Stats DataFrame and Combine 
if team_stats_list:
    team_stats_df = pd.DataFrame(team_stats_list, columns=all_player_column_names)
    final_result_df = pd.concat([result_df, team_stats_df], ignore_index=True)
    numeric_cols = final_result_df.select_dtypes(include=np.number).columns
    final_result_df[numeric_cols] = final_result_df[numeric_cols].round(4)

    print("\n--- Final Combined DataFrame (All Players and Teams) ---")
    print(final_result_df)

    try:
        final_result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\nSuccessfully saved final statistics to {output_path}")
    except Exception as e:
        print(f"\nError saving final results to CSV: {e}")

else:
    print("\nNo team statistics were calculated.")

# Made by Hung-dev-guy </Hng/>