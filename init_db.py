import psycopg2

# DATABASE_URL = 'postgresql-flexible-44314'
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

conn = psycopg2.connect(
    host="ec2-52-7-115-250.compute-1.amazonaws.com",
    database="dfmfctp63eg654",
    user="iyrxjafwmybqog",
    password="047647631db0ac1b3d727d7edd5b9e4c299586131585e1b6d41b2bc98e412521"
)
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(80) UNIQUE NOT NULL, password VARCHAR(80) NOT NULL, email VARCHAR(100) UNIQUE NOT NULL)
    """
)
cur.close()
conn.commit()