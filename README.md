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

<img width="1201" height="729" alt="1 -" src="https://github.com/user-attachments/assets/a34c0702-460b-408d-a5c0-d6224e994471" />
STEP 1 - Run the file "RUN - PyQtGUI.py"


<img width="1199" height="731" alt="2 -" src="https://github.com/user-attachments/assets/c9c505d9-c169-45ea-8f7b-dcf7fabe76ab" />
STEP 2 - Click "1. Import Library (XML)"

<img width="1201" height="731" alt="3 -" src="https://github.com/user-attachments/assets/615a2165-af59-4ab6-a08a-92144c2ec431" />
STEP 3 - Data will automatically be shown in the UI.

<img width="1199" height="727" alt="4 -" src="https://github.com/user-attachments/assets/5e69147e-52d0-4956-a942-11f9dff2f11c" />
STEP 4 - Submit your Email in the form. (This is required for API usage)


<img width="1196" height="725" alt="5 -" src="https://github.com/user-attachments/assets/bacac98c-60b3-42d8-bacc-2ec5537e8cae" />
STEP 5 - Click "2. Get Data from Cloud" (This can take time. Please wait)
You can also Refresh Table View to see which is the progress.

<img width="1192" height="716" alt="6 -" src="https://github.com/user-attachments/assets/f76a7102-4c9e-46c5-a27a-358cab914a14" />
STEP 6 - After finishing "Get Data from Cloud", you need to click 4. Push Metadata to Apple Music.

STEP 7 - You can now create a Smart Playlist based on the specific subgenres or instruments you need.





<img width="1404" height="1053" alt="7 -" src="https://github.com/user-attachments/assets/34c0e887-261b-43c1-90fe-647bd045ade7" />




