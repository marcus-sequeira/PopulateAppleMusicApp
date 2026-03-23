from getFromAPI import MusicBrainzClient
import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(SCRIPT_DIR, 'data', 'main.db')
print(f"Looking for database at: {db_path}")



class PopulateDatabase:
    def __init__(self, db_config, userEmail=None):
        self.userEmail = userEmail
        self.db_config = db_config
        self.musicbrainz = MusicBrainzClient(userEmail=self.userEmail)
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

    def populateDatabase(self):
        if not self.db_connection:
            raise Exception("Database connection is not established.")

        return True

    def populatePart1(self, optimization=True):
        cursor = self.db_connection.cursor()
        cursor2 = self.db_connection.cursor()
        rows = cursor.execute("SELECT Artist, Title, Album, ID FROM Library")
        recording_score = 0

        for artist, title, album, id in rows:
            print("Fetching data for", title, album, artist)
            try:
                if optimization:
                    cursor2.execute("SELECT track_id FROM TrackDetails WHERE track_id = ?", (id,))
                    if cursor2.fetchone():
                        continue
                recording_id, recording_score, release_group_id, release_id, releaseIDsDict, artistsIDsDict = self.musicbrainz.parsed_data_from_search_recording(title, album, artist, exact_search=False)

                cursor2.execute("INSERT OR IGNORE INTO ReleaseGroup (release_group_id, title, artist) " "VALUES (?,?,?)", (release_group_id, album, artist))
                cursor2.execute("INSERT OR IGNORE INTO TrackReleases (track_id, release_id) VALUES  (?, ?)", (id, release_id))
                cursor2.execute("INSERT OR IGNORE INTO TrackDetails (track_id, release_group_id)" "VALUES (?,?)", (id, release_group_id))

                try:
                    instruments = self.musicbrainz.getInstruments(recording_id)
                    if instruments:
                        for instrument in instruments:
                            print("Instruments", instrument)
                            if isinstance(instrument, list):
                                for i in instrument:
                                    cursor2.execute("INSERT OR IGNORE INTO Instruments (instrument_name) VALUES (?)",
                                                    (i,))
                                    cursor2.execute(
                                        "INSERT OR IGNORE INTO TrackInstruments (track_id, instrument_id) VALUES (?, (SELECT instrument_id FROM Instruments WHERE instrument_name = ?))",
                                        (id, i))
                            elif isinstance(instrument, str):
                                cursor2.execute("INSERT OR IGNORE INTO Instruments (instrument_name) VALUES (?)",
                                                (instrument,))
                                cursor2.execute(
                                    "INSERT OR IGNORE INTO TrackInstruments (track_id, instrument_id) VALUES (?, (SELECT instrument_id FROM Instruments WHERE instrument_name = ?))",
                                    (id, instrument))
                            else:
                                print(f"Unsupported instrument type: {type(instrument)} - {instrument}")
                except Exception as e:
                    print("Error getting instruments", e)
                    continue

                self.db_connection.commit()
            except Exception as e:
                print(title, album, artist, "Error", e)
                continue





    def populateGenres(self):
            print("Algorithm to find genres")
            cursor = self.db_connection.cursor()
            cursor2 = self.db_connection.cursor()
            previous = None
            rows = cursor.execute(
                "SELECT Artist, Title, Album, release_group_id FROM Library JOIN main.TrackDetails TD on Library.ID = TD.track_id")
            for artist, title, album, release_group_id in rows:
                print("Fetching data for", title, album, artist)
                if release_group_id != previous:
                    genres =self.musicbrainz.get_genresNames_for_release_group(release_group_id)
                    if genres:
                        for genre in genres:
                            cursor2.execute("INSERT OR IGNORE INTO Genres (genre_name) VALUES (?)", (genre,))
                            cursor2.execute("INSERT OR IGNORE INTO ReleaseGroupGenres (release_group_id, genre_id) VALUES (?, (SELECT genre_id FROM Genres WHERE genre_name = ?))", (release_group_id, genre))
                        self.db_connection.commit()
                    previous = release_group_id

    def checkExcludedTracks(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT ID, Title, Album, Artist FROM Library LEFT JOIN TrackDetails TD on Library.ID = TD.track_id WHERE release_group_id IS NULL")
        cursor2 = self.db_connection.cursor()
        rows2 = cursor2.execute("SELECT track_id FROM TrackDetails")
        rows = cursor.fetchall()
        excluded_count = 0
        included_count = 0
        for row in rows:
            print("Excluded track", row)
            excluded_count += 1
        print("Total excluded tracks", excluded_count)
        for row in rows2:
            included_count += 1
        print("Total included tracks", included_count)
        percentage = (excluded_count / (excluded_count + included_count)) * 100
        print("Percentage of excluded tracks", percentage)


if __name__ == '__main__':
    pd = PopulateDatabase(db_path)

    pd.checkExcludedTracks()
