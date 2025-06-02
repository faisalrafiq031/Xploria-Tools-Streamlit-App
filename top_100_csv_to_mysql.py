import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector

# Web scraping part (unchanged)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

url = "https://www.aixploria.com/en/top-100-ai/"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

top_100 = []

categories = soup.find_all('div', class_='trendai-grid-item')
if categories:
    for category in categories:
        title = category.find('h2')
        title = title.text.strip() if title else ""

        category_lists = category.find_all('div', class_='scrollable-content')
        for category_list in category_lists:
            for li in category_list.find_all('li'):
                category_item = {}
                category_href = li.find('a', {'class': 'site-review2', 'href': True})
                category_span = li.find('span', class_='stop-wordy')

                category_item['Category'] = title
                category_item['AI_Tool'] = category_span.text.strip() if category_span else ""
                category_item['URL'] = category_href['href'] if category_href else ""

                top_100.append(category_item)

df_categories = pd.DataFrame(top_100)

# Save to CSV (optional)
df_categories.to_csv("Top_100_2.csv", index=False)

# MySQL connection settings
host = 'localhost'
user = 'root'       # Change this to your MySQL username
password = 'Faisal$123'   # Change this to your MySQL password
database = 'Faisal_Data'
table_name = 'Top_100_AI_Tools'

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()

    # Create table if it doesn't exist
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        Category VARCHAR(255),
        AI_Tool VARCHAR(255),
        URL TEXT
    )
    """
    cursor.execute(create_table_query)

    # Insert data from DataFrame
    for index, row in df_categories.iterrows():
        # Avoid duplicates
        check_query = f"SELECT 1 FROM {table_name} WHERE Category = %s AND AI_Tool = %s AND URL = %s"
        cursor.execute(check_query, (row['Category'], row['AI_Tool'], row['URL']))
        if cursor.fetchone() is None:
            insert_query = f"INSERT INTO {table_name} (Category, AI_Tool, URL) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (row['Category'], row['AI_Tool'], row['URL']))

    conn.commit()
    print(f"Data successfully imported to MySQL table '{table_name}'")

except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
