import sqlite3

__all__ = (
	"RequestsDB",
)

class RequestsDB:
	"""
	DB object allowing to track the fizzbuzz requests in order
	to build a statistics page.

	This is a wrapper around sqlite3 exposing helpers to insert, update and retrieve
	requests information.

	Only valid requests are saved. A given request is represented by its parameters in the
	following order: "int1_int2_limit_str1_str2". The corresponding fizzbuzz sequense is
	saved along with the number of time the request was made.
	"""

	def __init__(self, database=".requests.db"):
		self.database = database
		self.connection = sqlite3.connect(database, check_same_thread=False)
		self._init_table()

	def _init_table(self):
		sql1 = """
			CREATE TABLE IF NOT EXISTS requests (
				id text PRIMARY KEY,
				sequence text,
				occurrence integer default 0
			)
		"""
		sql2 = """
			CREATE INDEX IF NOT EXISTS idx_occurence
			ON requests(occurrence)
		"""
		cur = self.connection.cursor()
		cur.execute(sql1)
		cur.execute(sql2)
		self.connection.commit()

	def add(self, reqId, seq, commit=True):
		sql1 = f"""
			INSERT OR IGNORE INTO requests (id, sequence)
			VALUES ("{reqId}", "{seq}")
		"""
		sql2 = f"""
			UPDATE requests
			SET occurrence = occurrence + 1
			WHERE id = "{reqId}"
		"""
		cur = self.connection.cursor()
		cur.execute(sql1)
		cur.execute(sql2)
		if commit:
			self.connection.commit()

	def get(self, reqId):
		sql = f"""
			SELECT sequence from requests
			WHERE id = "{reqId}"
		"""
		cur = self.connection.cursor()
		cur.execute(sql)
		return cur.fetchone()

	def get_most_hit(self, max_rows=10):
		sql = f"""
			SELECT id, sequence, occurrence FROM requests
			ORDER BY occurrence DESC
			LIMIT {max_rows}
		"""
		conn = sqlite3.connect(self.database, check_same_thread=False)
		cur = conn.cursor()
		cur.execute(sql)
		res = cur.fetchall()
		conn.close()
		return res
		
	def clear(self):
		"""
		Remove all rows in the db
		"""
		sql = "DELETE from requests"
		cur = self.connection.cursor()
		cur.execute(sql)
		self.connection.commit()

	def get_db_connection(self):
		return self.connection

