import os
from bs4 import BeautifulSoup
import csv
import re

filepath_profile = r"C:\DataAnalysis\Learned League"
file_name = 'LL Profile.htm'

filepath_match_days = os.path.join(filepath_profile, 'Match Days')
filepath_match_days_output = os.path.join(filepath_match_days, 'Output')

output_profile_data = []


full_path = os.path.join(filepath_profile, file_name)

with open(full_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

past_seasons_div = soup.find('div', class_='pastseasons')

all_seasons = past_seasons_div.find_all('div', class_='fl_latest')
for section in all_seasons:
    # Get season number
    h2 = section.find('h2')
    season = h2.text.strip() if h2 else 'Unknown'
    
    # Get rundle name
    h3 = section.find('h3')
    rundle = h3.text.strip() if h3 else 'Unknown'

    # Get match results from the table
    table = section.find('table', class_='std this_sea')
    if not table:
        continue
    
    
    rows = table.find_all('tr')[1:]  # Skip header row
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 6:
            continue

        cell_match_day, cell_opponent, cell_result, cell_score, cell_record, cell_rank = cells[:6]

        pf_match_day = cell_match_day.get_text(strip=True)
        pf_opponent  = cell_opponent.get_text(strip=True)
        pf_result    = cell_result.get_text(strip=True)
        pf_score     = cell_score.get_text(strip=True)
        pf_MatchID   = cell_score.find('a', href=True)['href'].split('=')[-1] if cell_score.find('a', href=True) else 'Unknown'
        pf_record    = cell_record.get_text(strip=True)
        pf_rank      = cell_rank.get_text(strip=True)

        output_profile_data.append({
            'File':      file_name,
            'Season':    season,
            'Rundle':    rundle,
            'Match Day': pf_match_day,
            'MatchID':   pf_MatchID,
            'Opponent':  pf_opponent,
            'Result':    pf_result,
            'Score':     pf_score,
            'Record':    pf_record,
            'Rank':      pf_rank
        })

        link_tag = cells[3].find('a', href=True)
        if link_tag:
            match_href = link_tag['href']  # e.g., "/match.php?id=10614631"
            match_id_match = re.search(r'id=(\d+)', match_href)
            if match_id_match:
                match_id = match_id_match.group(1)

                # Build local file path
                local_match_file = os.path.join(filepath_match_days, f"{match_id}.htm")

                if os.path.exists(local_match_file):
                    with open(local_match_file, 'r', encoding='utf-8') as match_file:
                        match_html = match_file.read()
                        match_soup = BeautifulSoup(match_html, 'html.parser')

                        # Find the QTable for Questions
                        qtable = match_soup.find('table', class_='QTable')
                        if not qtable:
                            print(f"No QTable found in {local_match_file}. Skipping.")
                            continue
                        
                        rows = qtable.find('tbody').find_all('tr')

                        match_file_name = os.path.basename(local_match_file)  #e.g., "123456.htm"
                        output_csv_md = os.path.join(filepath_match_days_output, match_file_name.replace('.htm', '_match_day_output.csv'))

                        with open(output_csv_md, 'w', newline='', encoding='utf-8') as f:
                            csv_writer = csv.writer(f, delimiter='\t')
                            csv_writer.writerow(['Q Number', 'Q Category','P1 Correct', 'P1 Points', 'P2 Correct', 'P2 Points', 'Avg Defense', 'Correct %'])
                            for row in rows:
                                cells = row.find_all('td')

                                q_number    = cells[0].get_text(strip=True).replace('.', '')                                
                                q_category  = cells[1].get_text(strip=True).split('—')[0].strip() #Unicode em-dash

                                p1_cell     = cells[2]
                                p1_text     = p1_cell.get_text(strip=True)
                                p1_correct  = 'ind-Yes2' in p1_cell.get('class', [])
                                p1_points   = int(p1_text) if p1_text.isdigit() else 0

                                p2_cell     = cells[3]
                                p2_text     = p2_cell.get_text(strip=True)
                                p2_correct  = 'ind-Yes2' in p2_cell.get('class', [])
                                p2_points   = int(p2_text) if p2_text.isdigit() else 0

                                avg_def_txt = cells[4].get_text(strip=True)
                                avg_defense = float(avg_def_txt)

                                correct_answer_text = cells[5].get_text(strip=True)
                                correct_answer_percent = correct_answer_text + '%'

                                csv_writer.writerow([
                                    q_number,
                                    q_category,
                                    p1_correct,
                                    p1_points,
                                    p2_correct,
                                    p2_points,
                                    avg_defense,
                                    correct_answer_percent
                                ])
                            print(f"✅ Done. Extracted to {output_csv_md}.")
            


# Write to CSV
output_csv_pf = os.path.join(filepath_profile, 'profile.csv')
with open(output_csv_pf, 'w', newline='', encoding='utf-8') as f:
    csv_writer = csv.DictWriter(f, fieldnames=output_profile_data[0].keys(), delimiter='\t')
    csv_writer.writeheader()
    csv_writer.writerows(output_profile_data)

print(f"✅ Done. Extracted {len(output_profile_data)} rows to {output_csv_pf}.")
