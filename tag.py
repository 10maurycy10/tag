import sqlite3

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

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

    def get_with_tag(self, tagname, value=None):
        cur = self.con.cursor()
        if value == None:
            cur.execute("SELECT filename FROM tagdb WHERE tagname=? GROUP BY filename;", (tagname, ));
        else:
            cur.execute("SELECT filename FROM tagdb WHERE tagname=? and data=? GROUP BY filename;", (tagname, value));
        return [f for f in cur]

    # TODO use sql for this.
    def get_with_tags(self, tags):
        matching = None
        for (key, value) in tags:
            filenames = self.get_with_tag(key, value=value)
            if matching == None:
                matching = filenames
            else:
                matching = intersection(matching, filenames)
        return matching


