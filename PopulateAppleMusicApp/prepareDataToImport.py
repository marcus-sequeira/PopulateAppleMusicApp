import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(SCRIPT_DIR, 'data', 'main.db')

class ImportDataToLibraryTable:
    def __init__(self, db_config):
        self.db_config = db_config
        self.db_connection = self.createDbConnection(db_config)

    def createDbConnection(self, db_config):
        try:
            if os.path.exists(db_config):
                conn = sqlite3.connect(db_config)
                print("Connected to the database.")
            else:
                print("Database does not exist.")
                return None
            return conn
        except sqlite3.Error as e:
            print('Could not connect to database.')
            return None

    def importInstrumentsToLibrary(self):
        cursor = self.db_connection.cursor()
        cursor2 = self.db_connection.cursor()
        cursor.execute("""
            SELECT ID, instrument_name 
            FROM Library 
            JOIN main.TrackDetails TD on Library.ID = TD.track_id 
            JOIN main.TrackInstruments TI on TD.track_id = TI.track_id 
            JOIN main.Instruments I on TI.instrument_id = I.instrument_id
        """)

        rows = cursor.fetchall()
        previous = None
        string_values = ""

        for id, instrument_name in rows:
            if id != previous:
                if previous is not None:
                    print(f"Track ID {previous}: {string_values}")
                    cursor2.execute("UPDATE Library SET Comments = ? WHERE ID = ?", (string_values, previous))

                string_values = instrument_name if instrument_name else ""
                previous = id
            else:
                if instrument_name:
                    string_values += ", " + instrument_name

        if previous is not None:
            print(f"Track ID {previous}: {string_values}")
            cursor2.execute("UPDATE Library SET Comments = ? WHERE ID = ?", (string_values, previous))
        self.db_connection.commit()

    def importSubgenresToLibrary(self):
        cursor = self.db_connection.cursor()
        cursor2 = self.db_connection.cursor()
        cursor.execute("""
            SELECT ID, genre_name FROM Library 
            JOIN main.TrackDetails TD on Library.ID = TD.track_id
            JOIN main.ReleaseGroup RG on RG.release_group_id = TD.release_group_id
            JOIN main.ReleaseGroupGenres RGG on RG.release_group_id = RGG.release_group_id
            JOIN main.Genres G on G.genre_id = RGG.genre_id

        """)

        rows = cursor.fetchall()
        previous = None
        string_values = ""

        for id, genre_name in rows:
            if id != previous:
                if previous is not None:
                    print(f"Track ID {previous}: {string_values}")
                    cursor2.execute("UPDATE Library SET Description = ? WHERE ID = ?", (string_values, previous))

                string_values = genre_name if genre_name else ""
                previous = id
            else:
                if genre_name:
                    string_values += ", " + genre_name

        if previous is not None:
            print(f"Track ID {previous}: {string_values}")
            cursor2.execute("UPDATE Library SET Description = ? WHERE ID = ?", (string_values, previous))
        self.db_connection.commit()

if __name__ == '__main__':
    importData = ImportDataToLibraryTable(DATABASE_PATH)
    importData.importInstrumentsToLibrary()
    importData.importSubgenresToLibrary()