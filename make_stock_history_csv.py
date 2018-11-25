import pandas as pd
import os

# Figure out where we are
dirname = os.path.dirname(__file__)
db_path = os.path.join(dirname, 'app.db')

# Read in the stock_price_history table
data = pd.read_sql_table("stock_price_history", 'sqlite:///' + os.path.join(dirname, 'app.db'), index_col="id")

# Cleaning up the data
data["price"] = data["price"].round(2)

# Make the long data wide instead - Note: Not implemented
# csv_data = data.pivot(index="name", columns="date", values="price")

# Output to CSV
csv_path = os.path.join(dirname, "app/static/stock_price_history.csv")
data.to_csv(csv_path)
