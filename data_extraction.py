import requests
import json
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# For global data

api_url = "https://api.apify.com/v2/key-value-stores/tVaYRsPHLjNdNBu7S/records/LATEST?disableRedirect=true."

response = requests.get(api_url)
if response.status_code == 200:
    covid_data = response.json()
    #print(covid_data)  # or process as needed
    #json_string=json.dumps(covid_data)
    #print(json_string[:100])
else:
    print("Failed to retrieve data")

# Assuming `json_data` is your JSON data
# Convert JSON string to a Python list if it's a string
covid_data = json.loads(covid_data) if isinstance(covid_data, str) else covid_data

# Create a DataFrame
df = pd.DataFrame(covid_data)

# Data Cleaning
df.replace('NA', None, inplace=True)
df['infected'] = pd.to_numeric(df['infected'], errors='coerce')
df['tested'] = pd.to_numeric(df['tested'], errors='coerce')
df['recovered'] = pd.to_numeric(df['recovered'], errors='coerce')
df['deceased'] = pd.to_numeric(df['deceased'], errors='coerce')

# Filter and select columns (adjust the list as needed)
columns_to_keep = ['infected', 'tested', 'recovered', 'deceased', 'country']
df = df[columns_to_keep]

# Additional transformations...
# For example, handling date conversions or extracting data from URLs

# Display the transformed data
#print(df.head())

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect('covid19_data.db')

# Define a table schema
# Adjust column types based on your data
create_table_query = '''
CREATE TABLE IF NOT EXISTS covid_stats (
    country TEXT,
    infected INTEGER,
    tested INTEGER,
    recovered INTEGER,
    deceased INTEGER
);
'''

# Create the table
conn.execute(create_table_query)


# Load data into the table
df.to_sql('covid_stats', conn, if_exists='replace', index=False)

# Example Query 1: Selecting data
query = "SELECT country, infected, recovered FROM covid_stats WHERE infected > 800000;"
df_infected = pd.read_sql_query(query, conn)
print(df_infected.head())

# Example Query 2: Aggregating data
query = "SELECT country, MAX(infected) as max_infected FROM covid_stats GROUP BY country;"
df_max_infected = pd.read_sql_query(query, conn)
print(df_max_infected.head())

# Plotting the maximum number of infected cases per country
df_max_infected.plot(kind='bar', x='country', y='max_infected', color='blue')
plt.title('Maximum Infected Cases per Country')
plt.xlabel('Country')
plt.ylabel('Infected Cases')
plt.xticks(rotation=45)
plt.show()

# Close the connection
conn.close()


