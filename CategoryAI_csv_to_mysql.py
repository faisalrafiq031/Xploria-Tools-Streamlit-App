import csv
import mysql.connector
from datetime import datetime

# MySQL Database configuration
DB_CONFIG = {
    'host': 'localhost',         # Replace with your MySQL server
    'user': 'root',   # Replace with your MySQL username
    'password': 'Faisal$123', # Replace with your MySQL password
    'database': 'Faisal_Data'    # Replace with your MySQL database name
}

TABLE_NAME = 'CategoryAI'
CSV_FILE_PATH = 'Category AI Tools Sheet.csv'  # Path to your CSV file

def create_db_connection():
    """Create and return a MySQL database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to MySQL database")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        return None

def create_table_if_not_exists(conn):
    """Create the table if it doesn't exist"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(255),
                `rank` VARCHAR(50),
                rating_score FLOAT,
                rating_stars INT,
                rating_value VARCHAR(100),
                tier VARCHAR(100),
                icon_url TEXT,
                title VARCHAR(255),
                tool_url TEXT,
                verified_icon TEXT,
                description TEXT,
                hashtags TEXT,
                upvote_icon TEXT,
                upvotes VARCHAR(50),
                visit_icon TEXT,
                visit_text VARCHAR(255),
                scraped_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print(f"✅ Table '{TABLE_NAME}' is ready")
    except mysql.connector.Error as err:
        print(f"❌ Failed to create table: {err}")

def read_csv_data(file_path):
    """Read data from CSV file and return as list of dictionaries"""
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        print(f"✅ Read {len(data)} records from CSV file")
        return data
    except Exception as e:
        print(f"❌ Failed to read CSV file: {e}")
        return None

def save_to_database(data, conn):
    """Save the CSV data to the database"""
    if not data or not conn:
        return

    try:
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            category, `rank`, rating_score, rating_stars, rating_value,
            tier, icon_url, title, tool_url, verified_icon, description,
            hashtags, upvote_icon, upvotes, visit_icon, visit_text
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for item in data:
            rating_score = float(item['rating_score']) if item['rating_score'] else None
            rating_stars = int(item['rating_stars']) if item['rating_stars'] else None

            cursor.execute(insert_query, (
                item['category'],
                item['rank'],
                rating_score,
                rating_stars,
                item['rating_value'],
                item['tier'],
                item['icon_url'],
                item['title'],
                item['tool_url'],
                item['verified_icon'],
                item['description'],
                item['hashtags'],
                item['upvote_icon'],
                item['upvotes'],
                item['visit_icon'],
                item['visit_text']
            ))

        conn.commit()
        print(f"✅ Saved {len(data)} records to database table '{TABLE_NAME}'")
    except mysql.connector.Error as err:
        print(f"❌ Failed to insert data: {err}")
        conn.rollback()

def main():
    conn = create_db_connection()
    if not conn:
        print("❌ Exiting due to connection failure")
        return

    create_table_if_not_exists(conn)

    data = read_csv_data(CSV_FILE_PATH)
    if not data:
        print("❌ Exiting due to CSV read failure")
        conn.close()
        return

    save_to_database(data, conn)
    conn.close()
    print("✅ CSV to MySQL import completed")

if __name__ == "__main__":
    main()
