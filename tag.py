import sqlite3

class TagDB:
    def __init__(self, filename):
        self.con = sqlite3.connect(filename)
        # Initalize the database
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS tagdb (filename TEXT, tagname TEXT, data text);")
        cur.execute("CREATE INDEX IF NOT EXISTS filenames ON tagdb (filename);")
        cur.execute("CREATE INDEX IF NOT EXISTS tagnames ON tagdb (tagname);")
        cur.execute("CREATE INDEX IF NOT EXISTS keyvalues ON tagdb (tagname, data);")

    def __del__(self):
        self.con.commit()

    def rm_file(self, filename):
        cur = self.con.cursor()
        cur.execute("DELETE FROM tagdb WHERE filename=?;", (filename,))

    def get_filenames(self) -> [str]:
        cur = self.con.cursor()
        cur.execute("SELECT filename FROM tagdb GROUP BY filename ORDER BY filename;")
        return [filename for (filename,) in cur]

    def get_tags(self, filename):
        cur = self.con.cursor()
        cur.execute("SELECT tagname,data FROM tagdb WHERE filename=?;", (filename,))
        return [tag for tag in cur]

    def set_tags(self, filename, tags):
        cur = self.con.cursor()
        cur.execute("DELETE FROM tagdb WHERE filename=?;", (filename,))
        cur = self.con.cursor()
        cur.executemany("INSERT INTO tagdb (filename, tagname, data) values (?, ?, ?)", [(filename, tag[0], tag[1]) for tag in tags])
