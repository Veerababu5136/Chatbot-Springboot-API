import requests
import re
import json  # Add this import
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import Workbook

# Function to fetch GeeksforGeeks user data
def fetch_gfg_user_data(gfg_username):
    try:
        url = f"https://www.geeksforgeeks.org/user/{gfg_username}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch the URL content for {gfg_username}.")
            return None

        # Extract JSON data using regex
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', response.text, re.DOTALL)
        if not match:
            return None

        json_data = match.group(1)
        user_info = json.loads(json_data)['props']['pageProps']['userInfo']

        # Parse problem categories using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        problem_categories = {}
        nodes = soup.find_all('div', class_='problemNavbar_head_nav--text__UaGCx')

        for node in nodes:
            category_match = re.match(r'([A-Za-z]+)\s*\((\d+)\)', node.get_text(strip=True))
            if category_match:
                category = category_match.group(1)
                count = category_match.group(2)
                problem_categories[category] = int(count)

        return {
            'name': user_info.get('name', 'N/A'),
            'score': user_info.get('score', 0),
            'totalProblemsSolved': user_info.get('total_problems_solved', 0),
            'problemCategories': problem_categories
        }
    except Exception as e:
        print(f"Error fetching GFG data: {e}")
        return None

# Function to read interns data from CSV file
def read_interns_from_csv(filename="interns.csv"):
    return pd.read_csv(filename)

# Function to save the results to an Excel file
def save_to_excel(data, filename="interns_data_with_scores.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Interns Data with Scores"

    # Set headers
    headers = ['S.No', 'Name', 'Batch No', 'Geeks Name', 'Score', 'Total Problems Solved', 'School', 'Basic', 'Easy', 'Medium', 'Hard']
    ws.append(headers)

    for index, row in enumerate(data, start=1):
        ws.append([
            index,
            row['geeks_name'],
            row['score'],
            row['totalProblemsSolved'],
            row['problemCategories'].get('SCHOOL', 0),
            row['problemCategories'].get('BASIC', 0),
            row['problemCategories'].get('EASY', 0),
            row['problemCategories'].get('MEDIUM', 0),
            row['problemCategories'].get('HARD', 0)
        ])

    wb.save(filename)
    print(f"Data saved to {filename}")

# Main function
def main():
    filename = input("Enter the CSV file name with interns data (e.g., 'interns.csv'): ")
    interns_data = read_interns_from_csv(filename)
    i = 0  # Initialize the counter to 0

    if not interns_data.empty:
        data_to_export = []
        for index, row in interns_data.iterrows():
            gfg_data = fetch_gfg_user_data(row['geeks_name'])
            if gfg_data:
                data_to_export.append({
                    'geeks_name': row['geeks_name'],
                    'score': gfg_data.get('score', 'N/A'),
                    'totalProblemsSolved': gfg_data.get('totalProblemsSolved', 0),
                    'problemCategories': gfg_data.get('problemCategories', {})
                })
            else:
                print(f"Failed to fetch data for {row['geeks_name']}")



        if data_to_export:
            save_to_excel(data_to_export)
        else:
            print("No data available to export.")
    else:
        print("No interns found in the CSV file.")

if __name__ == "__main__":
    main()
