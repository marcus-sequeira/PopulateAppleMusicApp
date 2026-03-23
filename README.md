# PopulateAppleMusicApp

PopulateAppleMusicApp is a Python-based desktop application designed to enrich your Apple Music library by automatically fetching and applying missing metadata, specifically focusing on subgenres and instruments.

By leveraging public APIs and macOS automation, this tool helps music enthusiasts organize their local libraries with detailed track information that Apple Music does not provide by default.

**Features**

* **XML Library Import:** Parses your exported iTunes/Apple Music XML library file to index your current tracks into a local SQLite database.
* **Automated Metadata Fetching:** Integrates with the MusicBrainz API to retrieve release groups, genres, and track instruments.
* **Smart Data Mapping:** Maps retrieved data to existing Apple Music fields:
    * Subgenres are injected into the track Description field.
    * Instruments are injected into the track Comments field.
* **Direct Apple Music Integration:** Uses native macOS AppleScript (osascript) to communicate with the Apple Music app, updating metadata in real-time using Persistent IDs.
* **GUI:** Provides a graphical user interface built with PyQt6 for managing the synchronization process, monitoring tables, and inputting API credentials.

**How it Works**

1.  **Import:** The application reads a library.xml file and populates a local main.db SQLite database with track, album, and artist information.
2.  **Sync (Cloud):** The app queries MusicBrainz to find missing subgenres, instruments, saving these to the local database.
3.  **Push:** The app executes AppleScripts to locate tracks in the Apple Music application and overwrites the Comments and Description fields with the retrieved data.

**Tech Stack**

* **Language:** Python 3
* **GUI Framework:** PyQt6
* **Database:** SQLite3
* **System Integration:** macOS AppleScript (osascript)
* **External APIs:** MusicBrainz and AcousticBrainz.
