"""
Identify the top 3 players with the highest and lowest scores for each statistic.
"""
import pandas as pd

file_path = r'C:\Users\Hungdever\Desktop\My_study\EPL\data\results.csv'
data = pd.read_csv(file_path)

statistics = [
                'Req_Age', 'Pltime_matches_played', 'Pltime_starts', 'Pltime_minutes',

                'Perf_goals', 'Perf_assists', 'Perf_yellow_cards', 'Perf_red_cards',

                'Exp_xG', 'Exp_xAG',

                'Prog_PrgC', 'Prog_PrgP', 'Prog_PrgR',

                'per90_Gls', 'per90_Ast', 'per90_xG', 'per90_xGA', 

                'GK_GA90', 'GK_Save%', 'GK_CS%', 'GK_PK_Save%',

                'Shoot_SoT%', 'Shoot_SoT/90', 'Shoot_G/Sh', 'Shoot_Dist',

                'Pass_Cmp', 'Pass_Cmp%', 'Pass_TotDist',
                'Pass_cpt_short', 'Pass_cpt_medium', 'Pass_cpt_long',
                'Pass_KP', 'Pass_1/3', 'Pass_PPA', 'Pass_CrsPA', 'Pass_PrgP', 

                'GnS_SCA', 'GnS_SCA90', 
                'GnS_GCA', 'GnS_GCA90',

                'Defen_Tkl', 'Defen_TklW',
                'Defen_Att', 'Defen_Lost', 
                'Defen_Blocks', 'Defen_Sh', 'Defen_Pass', 'Defen_Int',

                'Poss_touches', 'Poss_Def_Pen', 'Poss_Def_3rd', 'Poss_Mid_3rd', 'Poss_Att_3rd', 'Poss_Att_Pen',
                'Poss_Att','Poss_Succ%', 'Poss_Tkld%', 
                'Poss_Carries', 'Poss_PrgDist', 'Poss_PrgC', 'Poss_1/3', 'Poss_CPA', 'Poss_Mis', 'Poss_Dis',
                'Poss_Rec', 'Poss_PrgR',

                'Misc_Fls', 'Misc_Fld', 'Misc_Off', 'Misc_Crs', 'Misc_Recov',
                'Misc_Won', 'Misc_Lost', 'Misc_Won%'
            ]

results = {}
for stat in statistics:
    if stat in data.columns:
        data[stat] = pd.to_numeric(data[stat], errors='coerce')
        top_3_highest = data.nlargest(3, stat)[['player', stat]]
        top_3_lowest = data.nsmallest(3, stat)[['player', stat]]   
        results[stat] = {
            'highest': top_3_highest.values.tolist(),
            'lowest': top_3_lowest.values.tolist()
        }

output_file = r'c:\Users\Hungdever\Desktop\My_study\EPL\data\top_3.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    for stat, values in results.items():
        f.write(f"Statistic: {stat}\n")
        f.write("Top 3 Highest:\n")
        for player, value in values['highest']:
            f.write(f"  {player}: {value}\n")
        f.write("Top 3 Lowest:\n")
        for player, value in values['lowest']:
            f.write(f"  {player}: {value}\n")
        f.write("\n")

# Made by Hung-dev-guy </Hng/>