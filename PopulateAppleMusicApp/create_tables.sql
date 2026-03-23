CREATE TABLE IF NOT EXISTS Library (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title VARCHAR(256),
    Album VARCHAR(256),
    Artist VARCHAR(256),
    persistent_id VARCHAR(16) UNIQUE,
    BPM INT,
    Category VARCHAR(256),
    Comments VARCHAR(256),
    Description VARCHAR(256),
    Genre VARCHAR(256),
    Grouping VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS TrackDetails (
    track_id INTEGER PRIMARY KEY,
    release_group_id CHAR(36),
    FOREIGN KEY (release_group_id) REFERENCES ReleaseGroup(release_group_id),
    FOREIGN KEY (track_id) REFERENCES Library(ID)
);

CREATE TABLE IF NOT EXISTS TrackReleases(
    track_id INTEGER,
    release_id CHAR(36),
    FOREIGN KEY (track_id) REFERENCES TrackDetails(track_id)

);

CREATE TABLE IF NOT EXISTS Genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ReleaseGroupGenres (
    release_group_id CHAR(36),
    genre_id INTEGER,
    PRIMARY KEY (release_group_id, genre_id),
    FOREIGN KEY (release_group_id) REFERENCES ReleaseGroup(release_group_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE IF NOT EXISTS Instruments (
    instrument_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS TrackInstruments (
    track_id INTEGER,
    instrument_id INTEGER,
    PRIMARY KEY (track_id, instrument_id),
    FOREIGN KEY (track_id) REFERENCES TrackDetails(track_id),
    FOREIGN KEY (instrument_id) REFERENCES Instruments(instrument_id)
);


CREATE TABLE IF NOT EXISTS ReleaseGroup (
    release_group_id CHAR(36) PRIMARY KEY,
    title VARCHAR(256),
    artist VARCHAR(256),
    release_date DATE
);

