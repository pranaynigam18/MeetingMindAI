import psycopg2


conn = psycopg2.connect(
    host="localhost",
    database="meetingmind",
    user="postgres",
    password="Delhi2026"
)

cursor = conn.cursor()