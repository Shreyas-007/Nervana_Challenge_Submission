from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///commands.db')
session = sessionmaker(bind=engine)()

'''
print engine.table_names()
session.add()


conn = engine.connect()
stmt = "CREATE TABLE Employees(Emp_Name VARCHAR(10))"

result = conn.execute(stmt)

print result.fetchall()

'''