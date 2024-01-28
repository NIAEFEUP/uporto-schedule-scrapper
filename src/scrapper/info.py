from database.Database import Database
from datetime import datetime

print("Saving scrapper info...")
db = Database() 
db.insert('info', {'date': datetime.now()})
db.connection.close()