import pandas as pd
import sys 
import csv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def read_csv_safe(filepath, required_cols=None):
    df = pd.read_csv(filepath)
    if required_cols:
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Error: Missing required columns in '{filepath}': {missing_cols}")
            print(f"Columns found: {df.columns.tolist()}")
            sys.exit(1) 
    return df

def standardize_player_name(name_series):
    split_name = name_series.astype(str).str.split('    ').str[0]
    return split_name.str.lower()
 

if __name__ == '__main__':
    df_results = read_csv_safe(r'C:\Users\Hungdever\Desktop\My_study\EPL\data\results.csv', required_cols=['player', 'Pltime_minutes'])
    df_results['Pltime_minutes'] = pd.to_numeric(df_results['Pltime_minutes'], errors='coerce')
    df_results.dropna(subset=['Pltime_minutes'], inplace=True)
    df_results['Pltime_minutes'] = df_results['Pltime_minutes'].astype(int)
    players_filtered = df_results[df_results['Pltime_minutes'] > 900].copy() 
    print(f"\nFiltered {len(players_filtered)} players with minutes played > 900.")

    df_etv = read_csv_safe(r'C:\Users\Hungdever\Desktop\My_study\EPL\data\ETV_list.csv', required_cols=['Player Name','ETV'])
    
    # Standardize player names for vectorization
    players_filtered['std_name'] = standardize_player_name(players_filtered['player'])
    df_etv['std_name'] = df_etv['Player Name'].str.lower()

    # Initialize SentenceTransformer model (BERT-based) and vectorize names
    model = SentenceTransformer("all-MiniLM-L6-v2")
    player_names = players_filtered['std_name'].tolist()
    etv_names = df_etv['std_name'].tolist()
    player_embeddings = model.encode(player_names)
    etv_embeddings = model.encode(etv_names)

    # Compute cosine similarity between each player's name and each ETV name
    similarity_matrix = cosine_similarity(player_embeddings, etv_embeddings)
    raw_player_names = players_filtered['player']
    # Print the best match for each player based on cosine similarity
    best_matches = []
    for i, player in enumerate(player_names):
        best_match_idx = similarity_matrix[i].argmax()
        best_match_name = etv_names[best_match_idx]
        best_similarity = similarity_matrix[i][best_match_idx]
        ETV = df_etv['ETV'][best_match_idx]
        best_matches.append({
            'player': player,
            'best_etv_match': best_match_name,
            'cosine_similarity': best_similarity,
            'Player Name': raw_player_names.iloc[i],
            'ETV': ETV
        })
        print(f"Player: {player} -> Best match in ETV_list: {best_match_name} (Cosine similarity: {best_similarity:.3f})")

    df_best_matches = pd.DataFrame(best_matches)
    output = r'C:\Users\Hungdever\Desktop\My_study\EPL\data\EX4-p1-results-bertcos.csv'
    df_best_matches.to_csv(output, index=False, encoding='utf-8')
    print("Complete writing data to CSV file!")

