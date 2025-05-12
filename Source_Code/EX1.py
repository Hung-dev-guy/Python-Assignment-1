"""
Scraper for EPL data from fbref.com
"""

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import numpy as np
import logging
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class FootballDataScraper:
    RootURL = "https://fbref.com"
    LeagueURL = "https://fbref.com/en/comps/9/Premier-League-Stats"
    
    TABLE_IDENTIFIERS_FBREF = {
        'standard': 'stats_standard_9', 'shooting': 'stats_shooting_9',
        'passing': 'stats_passing_9', 'gca': 'stats_gca_9',
        'defense': 'stats_defense_9', 'possession': 'stats_possession_9',
        'misc': 'stats_misc_9', 'keeper': 'stats_keeper_9',
    }

    STAT_DEFINITIONS = {
        'basic': {
            'Req_Nation': {'attr': 'nationality', 'numeric': False},
            'Req_Position': {'attr': 'position', 'numeric': False},
        },
        'playing_time': {
            'Pltime_matches_played': {'attr': 'games', 'numeric': True},
            'Pltime_starts': {'attr': 'games_starts', 'numeric': True},
            'Pltime_minutes': {'attr': 'minutes', 'numeric': True},
        },
        'performance': {
            'Perf_goals': {'attr': 'goals', 'numeric': True}, 'Perf_assists': {'attr': 'assists', 'numeric': True},
            'Perf_yellow_cards': {'attr': 'cards_yellow', 'numeric': True}, 'Perf_red_cards': {'attr': 'cards_red', 'numeric': True},
        },
        'expected': {
            'Exp_xG': {'attr': 'xg', 'numeric': True}, 'Exp_xAG': {'attr': 'xg_assist', 'numeric': True},
        },
        'progression': {
            'Prog_PrgC': {'attr': 'progressive_carries', 'numeric': True}, 'Prog_PrgP': {'attr': 'progressive_passes', 'numeric': True},
            'Prog_PrgR': {'attr': 'progressive_passes_received', 'numeric': True},
        },
        'per_90': {
            'per90_Gls': {'attr': 'goals_per90', 'numeric': True}, 'per90_Ast': {'attr': 'assists_per90', 'numeric': True},
            'per90_xG': {'attr': 'xg_per90', 'numeric': True}, 'per90_xGA': {'attr': 'xg_assist_per90', 'numeric': True},
        },
        'goalkeeping': {
            'GK_GA90': {'attr': 'gk_goals_against_per90', 'numeric': True}, 'GK_Save%': {'attr': 'gk_save_pct', 'numeric': True},
            'GK_CS%': {'attr': 'gk_clean_sheets_pct', 'numeric': True}, 'GK_PK_Save%': {'attr': 'gk_pens_save_pct', 'numeric': True},
        },
        'shooting': {
            'Shoot_SoT%': {'attr': 'shots_on_target_pct', 'numeric': True}, 'Shoot_SoT/90': {'attr': 'shots_on_target_per90', 'numeric': True},
            'Shoot_G/Sh': {'attr': 'goals_per_shot', 'numeric': True}, 'Shoot_Dist': {'attr': 'average_shot_distance', 'numeric': True},
        },
        'passing': {
            'Pass_Cmp': {'attr': 'passes_completed', 'numeric': True}, 'Pass_Cmp%': {'attr': 'passes_pct', 'numeric': True},
            'Pass_TotDist': {'attr': 'passes_total_distance', 'numeric': True}, 'Pass_cpt_short': {'attr': 'passes_pct_short', 'numeric': True},
            'Pass_cpt_medium': {'attr': 'passes_pct_medium', 'numeric': True}, 'Pass_cpt_long': {'attr': 'passes_pct_long', 'numeric': True},
            'Pass_KP': {'attr': 'assisted_shots', 'numeric': True}, 'Pass_1/3': {'attr': 'passes_into_final_third', 'numeric': True},
            'Pass_PPA': {'attr': 'passes_into_penalty_area', 'numeric': True}, 'Pass_CrsPA': {'attr': 'crosses_into_penalty_area', 'numeric': True},
            'Pass_PrgP': {'attr': 'progressive_passes', 'numeric': True}
        },
        'goal_shot_creation': {
            'GnS_SCA': {'attr': 'sca', 'numeric': True}, 'GnS_SCA90': {'attr': 'sca_per90', 'numeric': True},
            'GnS_GCA': {'attr': 'gca', 'numeric': True}, 'GnS_GCA90': {'attr': 'gca_per90', 'numeric': True},
        },
        'defensive': {
            'Defen_Tkl': {'attr': 'tackles', 'numeric': True}, 'Defen_TklW': {'attr': 'tackles_won', 'numeric': True},
            'Defen_Att': {'attr': 'challenges_tackles', 'numeric': True}, 'Defen_Lost': {'attr': 'challenges_lost_pct', 'numeric': True}, # Hoặc challenges_lost
            'Defen_Blocks': {'attr': 'blocks', 'numeric': True}, 'Defen_Sh': {'attr': 'blocked_shots', 'numeric': True},
            'Defen_Pass': {'attr': 'blocked_passes', 'numeric': True}, 'Defen_Int': {'attr': 'interceptions', 'numeric': True},
        },
        'possession': {
            'Poss_touches': {'attr': 'touches', 'numeric': True}, 'Poss_Def_Pen': {'attr': 'touches_def_pen_area', 'numeric': True},
            'Poss_Def_3rd': {'attr': 'touches_def_3rd', 'numeric': True}, 'Poss_Mid_3rd': {'attr': 'touches_mid_3rd', 'numeric': True},
            'Poss_Att_3rd': {'attr': 'touches_att_3rd', 'numeric': True}, 'Poss_Att_Pen': {'attr': 'touches_att_pen_area', 'numeric': True},
            'Poss_Att': {'attr': 'touches_att_3rd', 'numeric': True}, 'Poss_Succ%': {'attr': 'take_ons_won_pct', 'numeric': True},
            'Poss_Tkld%': {'attr': 'take_ons_tackled_pct', 'numeric': True}, 'Poss_Carries': {'attr': 'carries', 'numeric': True},
            'Poss_PrgDist': {'attr': 'carries_progressive_distance', 'numeric': True}, 'Poss_PrgC': {'attr': 'progressive_carries', 'numeric': True}, 
            'Poss_1/3': {'attr': 'carries_into_final_third', 'numeric': True }, 'Poss_CPA': {'attr': 'carries_into_penalty_area', 'numeric': True}, 
            'Poss_Mis': {'attr': 'miscontrols', 'numeric': True}, 'Poss_Dis': {'attr': 'dispossessed', 'numeric': True}, 
            'Poss_Rec': {'attr': 'passes_received', 'numeric': True}, 'Poss_PrgR': {'attr': 'progressive_passes_received', 'numeric': True}
        },
        'miscellaneous': {
            'Misc_Fls': {'attr': 'fouls', 'numeric': True}, 'Misc_Fld': {'attr': 'fouled', 'numeric': True},
            'Misc_Off': {'attr': 'offsides', 'numeric': True}, 'Misc_Crs': {'attr': 'crosses', 'numeric': True},
            'Misc_Recov': {'attr': 'ball_recoveries', 'numeric': True}, 'Misc_Won': {'attr': 'aerials_won', 'numeric': True},
            'Misc_Lost': {'attr': 'aerials_lost', 'numeric': True}, 'Misc_Won%': {'attr': 'aerials_won_pct', 'numeric': True},
        }
    }
    TABLE_CATEGORY_TO_STATS_GROUPS = {
        'standard': ['basic', 'playing_time', 'performance', 'per_90', 'expected', 'progression'],
        'keeper': ['goalkeeping'], 'shooting': ['shooting'], 'passing': ['passing'],
        'gca': ['goal_shot_creation'], 'defense': ['defensive'], 'possession': ['possession'], 'misc': ['miscellaneous']
    }

    def __init__(self):
        self.Collected_data = []
        self.browser = None
        self.Init_browser()

    def Init_browser(self):
        opts = uc.ChromeOptions()
        opts.add_argument('--headless=new')
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        try:
            self.browser = uc.Chrome(options=opts)
            self.browser.set_window_size(1920, 1080)
            logger.info("Browser initialized.")
        except Exception as e:
            logger.error(f"Browser initialization failed: {e}", exc_info=True); raise

    def fetch_page_content(self, url, max_attempts=3):
        if not self.browser: return None
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Fetching {url} (Attempt {attempt+1})")
                self.browser.get(url)
                time.sleep(random.uniform(3, 5))
                WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table[id^='stats_']")))
                time.sleep(random.uniform(1, 2))
                return BeautifulSoup(self.browser.page_source, 'html.parser')
            except Exception as e:
                if attempt < max_attempts - 1: 
                    time.sleep(random.uniform(5, 8))
        logger.error(f"Failed to fetch {url} after {max_attempts} attempts.")
        return None

    def gather_team_urls(self):
        logger.info(f"Gathering team URLs from: {self.LeagueURL}")
        page = self.fetch_page_content(self.LeagueURL)
        if not page: return []
        urls = set()

        table = page.find('table', id=lambda x: x and 'results' in x and 'overall' in x) or page.find('table', class_='stats_table')
        if not table: 
            logger.error("League table not found.") 
            return []
        for a in table.select('tbody tr td[data-stat="team"] a[href*="/squads/"]'):
            if '/history/' not in a.get('href', ''): 
                urls.add(urljoin(self.RootURL, a['href']))
        logger.info(f"Found {len(urls)} team URLs.")
        return list(urls)

    def extract_statistic(self, row, stat_name, is_numeric=False):
        cell = row.select_one(f'td[data-stat="{stat_name}"], th[data-stat="{stat_name}"]')
        if not cell or not cell.text.strip() or cell.text.strip() == '-': 
            return "N/a"
        val = cell.text.strip()
        if is_numeric:
            try: 
                return float(val.replace(',', '').replace('%', '')) if val.replace(',', '').replace('%', '') else "N/a"
            except ValueError: 
                return "N/a"
        return val

    def _apply_stat_extraction(self, row, p_data, stat_group_name):
        if stat_group_name == 'basic': 
            p_data['Req_Nation'] = self.extract_statistic(row, self.STAT_DEFINITIONS['basic']['Req_Nation']['attr'], False)
            p_data['Req_Position'] = self.extract_statistic(row, self.STAT_DEFINITIONS['basic']['Req_Position']['attr'], False)
            age_str = self.extract_statistic(row, 'age')
            if isinstance(age_str, str) and '-' in age_str: 
                p_data['Req_Age'] = int(age_str.split('-')[0]) if age_str.split('-')[0].isdigit() else "N/a"
            elif age_str != "N/a" and age_str.isdigit(): 
                p_data['Req_Age'] = int(age_str)
            else: 
                p_data['Req_Age'] = "N/a"
            return 
        
        for key, defs in self.STAT_DEFINITIONS.get(stat_group_name, {}).items():
            p_data[key] = self.extract_statistic(row, defs['attr'], defs['numeric'])

    def locate_stat_tables(self, page_content):
        table_map = {}
        all_found = {tbl.get('id'): tbl for tbl in page_content.find_all('table', id=True) if tbl.get('id','').startswith('stats_')}
        for cat, expected_id_pattern in self.TABLE_IDENTIFIERS_FBREF.items():
            if expected_id_pattern in all_found:
                table_map[cat] = all_found[expected_id_pattern]
            else: 
                for found_id, table_obj in all_found.items():
                    if cat in found_id and table_obj not in table_map.values(): 
                        table_map[cat] = table_obj; break
        if not table_map: 
            logger.warning("Could not locate any specific stat tables via predefined IDs.")
        return table_map

    def compile_player_stats(self, table, cat_name, club):
        records = []
        tbody = table.find('tbody')
        if not tbody: return []
        groups = self.TABLE_CATEGORY_TO_STATS_GROUPS.get(cat_name, [])
        if not groups: return []

        for r_idx, row in enumerate(tbody.find_all('tr', class_=lambda x: x != 'thead' and x != 'spacer' and not (x and 'hidden' in x))):
            p_cell = row.select_one('th[data-stat="player"], td[data-stat="player"]')
            if not p_cell or not p_cell.text.strip() or p_cell.text.strip().lower() in ["squad total", "opponent total", "player"]: continue
            p_name = p_cell.text.strip()
            p_data = {'player': p_name, 'team': club}
            try:
                for group in groups: self._apply_stat_extraction(row, p_data, group)
                records.append(p_data)
            except Exception as e: logger.error(f"Err processing {p_name} ({club}) in {cat_name}: {e}", exc_info=True)
        return records

    def process_team_data(self, url):
        logger.info(f"Processing team: {url}")
        page = self.fetch_page_content(url)
        if not page: return []
        name_el = page.select_one('h1[itemprop="name"] span')
        club = name_el.text.strip().split(" Stats")[0] if name_el and name_el.text.strip() else page.title.text.split(" Stats")[0].split(" | ")[0]
        logger.info(f"Club: {club}")
        
        tables = self.locate_stat_tables(page)
        if not tables: logger.warning(f"No tables for {club} ({url})"); return []
        
        merged_data = {}
        order = ['standard'] + [c for c in self.TABLE_IDENTIFIERS_FBREF if c != 'standard' and c in tables]
        for cat_name in order:
            if cat_name not in tables: continue
            logger.debug(f"Compiling '{cat_name}' for {club}")
            for p_stats in self.compile_player_stats(tables[cat_name], cat_name, club):
                p_name = p_stats.get('player')
                if p_name: merged_data.setdefault(p_name, {}).update(p_stats)
        return list(merged_data.values())

    def execute_scraping(self):
        logger.info("--- Starting scraping ---")
        all_data = []
        try:
            team_urls = self.gather_team_urls()
            if not team_urls: logger.error("No team URLs. Terminating."); return None
            
            for i, url in enumerate(team_urls):
                all_data.extend(self.process_team_data(url))
                if i < len(team_urls) - 1: time.sleep(random.uniform(3, 6))

            if not all_data: 
                logger.warning("No data collected.")
                return pd.DataFrame()
            df = pd.DataFrame(all_data).replace(["N/a", "", None], np.nan)
            logger.info(f"Initial df shape: {df.shape}")

            num_cols = ['Req_Age'] + [col for group in self.STAT_DEFINITIONS.values() for col,p in group.items() if p.get('numeric')]
            for col in list(set(num_cols)): 
                if col in df.columns and df[col].dtype == 'object': df[col] = pd.to_numeric(df[col], errors='coerce')
            
            if 'Pltime_minutes' in df.columns and pd.api.types.is_numeric_dtype(df['Pltime_minutes']):
                df.dropna(subset=['Pltime_minutes'], inplace=True)
                df = df[df['Pltime_minutes'] > 90].copy()
                logger.info(f"Filtered by minutes > 90. New shape: {df.shape}")
            
            if 'player' in df.columns:
                df['player'] = df['player'].astype(str)
                df.sort_values(by='player', inplace=True, ignore_index=True, key=lambda c: c.str.lower())

            core = ['player','team','Req_Nation','Req_Position','Req_Age','Pltime_matches_played','Pltime_starts','Pltime_minutes']
            ordered = [c for c in core if c in df.columns] + sorted([c for c in df.columns if c not in core])
            df = df[ordered]

            out_dir = os.path.join(os.path.expanduser("~"), "Desktop", "EPL_Data_Output") 
            os.makedirs(out_dir, exist_ok=True)

            out_path = os.path.join(out_dir, r'C:\Users\Hungdever\Desktop\My_study\EPL\data\results.csv')
            df.to_csv(out_path, index=False, encoding='utf-8-sig', na_rep='N/a')
            logger.info(f"Data saved to {out_path}")
            return df
        except Exception as e: logger.error(f"Scraping execution error: {e}", exc_info=True); return None
        finally:
            if self.browser: logger.info("--- Terminating browser ---"); self.browser.quit()

if __name__ == "__main__":
    logger.info("========= Start Scraper =========")
    s_time = time.time()
    scraper = FootballDataScraper()
    if scraper.browser: 
        scraper.execute_scraping()
    else: 
        logger.error("Browser init failed.")
    logger.info(f"Total time: {time.time() - s_time:.2f}s. ========= End Scraper =========")

    # Made by Hung-dev-guy </Hng/>