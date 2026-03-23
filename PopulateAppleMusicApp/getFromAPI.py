import time
import requests

class MusicBrainzClient:
    BASE_URL = "https://musicbrainz.org/ws/2/"

    def __init__(self, fmt="json", sleep_time=0.3, userEmail=None):
        self.fmt = fmt
        self.sleep_time = sleep_time

        self.headers = {
            "User-Agent": f"PopulateAppleMusicApp/1.1 ({userEmail})"
        }
        print(f"!!!!!!!!!!!! userEmail é {userEmail}")

    def _make_request(self, endpoint, params):
        time.sleep(self.sleep_time)

        url = f"{self.BASE_URL}{endpoint}"
        params['fmt'] = self.fmt  
        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}")

    def get_release(self, release_id):
        endpoint = f"release/{release_id}"
        params = {}
        return self._make_request(endpoint, params)

    def get_artist(self, artist_id):
        return self._make_request("artist", {"artist": artist_id})

    def get_area(self, area_id):
        return self._make_request("area", {"area": area_id})

    def get_label(self, label_id):
        return self._make_request("label", {"label": label_id})

    def extractGenresList(self, release_group_id):
        data = self.get_genresNames_for_release_group(release_group_id)
        names = [item['name'] for item in data]
        return names

    def get_recordingArtistRels(self, recording_id):
        endpoint = f"recording/{recording_id}"
        params = {
            "inc": "artist-rels",  
        }
        return self._make_request(endpoint, params)

    def search_release(self, album_title, artist_name, exact_search=True):
        endpoint = "release/"
        if exact_search:
            query = f"release:\"{album_title}\" AND artist:\"{artist_name}\""
        else:
            query = f"release:{album_title} AND artist:{artist_name}"

        params = {'query': query}

        return self._make_request(endpoint, params)

    def search_recording(self, track_name ,album_title, artist_name, exact_search=True):
        endpoint = "recording/"
        if exact_search:
            query = f"artist:\"{artist_name}\" AND release:\"{album_title}\" AND recording:\"{track_name}\""
        else:
            query = f"artist:{artist_name} AND release:{album_title} AND recording:{track_name}"

        params = {'query': query}

        return self._make_request(endpoint, params)

    def parsed_data_from_search_recording(self, track_name, album_title, artist_name, exact_search=False, recording_index=0):
        data = self.search_recording(track_name, album_title, artist_name, exact_search)
        releaseIDsDict = {}
        artistsIDsDict = {}
        releasesIDsList = []
        release_group_id = None
        release_id = None

        if 'recordings' in data:
            recording = data['recordings'][recording_index]
            recording_id = recording['id']
            recording_score = recording['score']
            if 'releases' in recording:
                for release in recording.get('releases', []):
                    release_group_id = release['release-group']['id']
                    release_id = release['id']
                    releaseIDsDict[release_id] = release['title']

                    for credit in release.get('artist-credit', []):
                        artist_id = credit['artist']['id']
                        artist_name = credit['artist']['name']
                        artistsIDsDict[artist_id] = artist_name

                return recording_id, recording_score, release_group_id, release_id, releaseIDsDict, artistsIDsDict


    def parsed_data_from_release(self, album_title, artist_name, exact_search=True):
        data = self.search_release(album_title, artist_name, exact_search)
        releaseIDsDict = {}
        artistsIDsDict = {}
        releasesIDsList = []
        if 'releases' in data:
            for release in data['releases']:
                releasesIDsList.append(release['id'])
                release_group = release.get('release-group', {})
                release_group_id = release_group.get('id', 'Unknown ID')
                release_group_title = release_group.get('title', 'Unknown Title')
                release_id = release['id']  
                release_title = release.get('title', 'Unknown Title')
                releaseIDsDict[release_id] = release_title

                for credit in release.get('artist-credit', []):
                    artist_id = credit['artist']['id']
                    artist_name = credit['artist']['name']
                    artistsIDsDict[artist_id] = artist_name

        return release_group_id, artistsIDsDict, releasesIDsList


    def get_recordingData(self, artist_name, track_name):
        query = f"artist:{artist_name} AND recording:{track_name}"
        return self._make_request("recording", {"query": query})

    def search_release_group_by_artist_and_name(self, artist_name, release_name):
        query = f"artist:{artist_name} release:{release_name}"
        params = {"query": query}

        return self._make_request("release-group", params)

    def search_release_group_by_artist_and_name(self, artist_name, release_name):
        query = f"artist:{artist_name} release:{release_name}"
        params = {"query": query}

        return self._make_request("release-group", params)

    def extract_ids_from_recording(self, artist_name, track_name):
        data = self.get_recordingData(artist_name, track_name)
        artistIDs = []
        album_id = None
        song_id = None
        recording_id = None
        if 'recordings' in data:
            for item in data['recordings']:
                if 'artist-credit' in item:
                    for artist in item['artist-credit']:
                        if 'artist' in artist and 'id' in artist['artist']:
                            artistIDs.append(artist['artist']['id'])

                if 'releases' in item and item['releases']:
                    album_id = item['releases'][0]['id']
                if 'id' in item:
                    song_id = item['id']  

                if artistIDs and album_id and song_id:
                    print(f"Artist IDs: {artistIDs}")
                    print(f"Album ID: {album_id}")
                    print(f"Song ID: {song_id}")

                    return artistIDs, album_id, song_id

        return artistIDs, album_id, song_id

    def getReleaseGroupIDfromRelease(self, artist_name, release_name):
        data = self.search_release_group_by_artist_and_name(artist_name, release_name)
        release_group_id = data['release-groups'][0]['id']
        return release_group_id, data

    def get_genresNames_for_release_group(self, release_group_id):
        url = f"{self.BASE_URL}release-group/{release_group_id}?inc=genres&fmt={self.fmt}"
        release_group_genres = []
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json() if self.fmt == "json" else response.text

            if self.fmt == "json":
                genres = data.get('genres', [])
                for genre in genres:
                    release_group_genres.append(genre['name'])
                return release_group_genres
            else:
                return data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def get_release_group_releases(self, release_group_id):
        endpoint = f"release-group/{release_group_id}"
        params = {
            'inc': 'releases',
        }
        return self._make_request(endpoint, params)


    def get_Recordings(self, release_id):
        endpoint = f"release/{release_id}"
        params = {
            'inc' : 'recordings'
        }
        return self._make_request(endpoint, params)

    def extractTracksFromRecordings(self, release_id):
        recordings = self.get_Recordings(release_id)
        recording_dict = {}
        for recording in recordings['media']:
            for track in recording['tracks']:
                recording_id = track['recording']['id']
                recording_title = track['title']
                recording_dict[recording_id] = recording_title
        return recording_dict

    def getInstruments(self, recording_id):
        data = self.get_recordingArtistRels(recording_id)
        instrumentsList = []
        for relations in data['relations']:
            if relations['attributes'] in instrumentsList or not relations['attributes']:
                continue
            instrumentsList.append(relations['attributes'])
        return instrumentsList

def get_musicbrainz_recording_id(artist, song):
    url = f'https://musicbrainz.org/ws/2/recording/?query=artist:{artist}%20AND%20recording:{song}&fmt=json'

    try:
        response = requests.get(url)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            print("Error: Failed to decode JSON response.")
            return None

        if "recordings" in data and data["recordings"]:
            mbid = data["recordings"][0]["id"]
            return mbid
        else:
            print("Song not found in MusicBrainz.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_low_level_features(mbid):
    url = f'https://acousticbrainz.org/{mbid}/low-level'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data for MBID {mbid}. Status code: {response.status_code}")
        return None
        
def parseBPMfromMBdata(data):
    def convertToInteger(value):
        if type(value) is list:
            return value[0]
        return value

    if isinstance(data, dict):
        for key, value in data.items():
            if key == "bpm":
                return value  
            else:
                result = parseBPMfromMBdata(value)
                if result is not None:
                    return convertToInteger(result)  
    elif isinstance(data, list):
        for item in data:
            result = parseBPMfromMBdata(item)
            if result is not None:
                return convertToInteger(result)  
    return None  

def getBPMfromMBapi(artist, song):
    mbid = get_musicbrainz_recording_id(artist, song)
    data = get_low_level_features(mbid)
    bpm = parseBPMfromMBdata(data)
    return bpm

def create_deezer_search_url(query):
    formatted_query = query.replace(' ', '+')
    url = f"https://api.deezer.com/search?q={formatted_query}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get('data', [])

        if data:
            return data[0].get('id', None)
        else:
            return None
    else:
        return f"Error: {response.status_code}"

def get_track_info(track_id):
    url = f"https://api.deezer.com/track/{track_id}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}"

def getBPM_FromDeezer(track_id):
    try:
        response = get_track_info(track_id)
        return response.get('bpm', None)
    except Exception as e:
        print(f"Error: {e}")
        return None

def getBPMfromDeezerApi(artist, song):
    artistSong = artist + " " + song
    id = create_deezer_search_url(artistSong)
    bpm = getBPM_FromDeezer(id)
    return bpm

if __name__ == '__main__':
    musicbrainz = MusicBrainzClient()

    artist = "Bladee"
    album = "Cold Visions"
    track = "Wodrainer"

    recording_id, recording_score, release_group_id, release_id, releaseIDsDict, artistsIDsDict = musicbrainz.parsed_data_from_search_recording(track, album, artist, True, 0)
    print(f"Recording ID: {recording_id}")
    print(f"Recording Score: {recording_score}")
    print(f"Release Group ID: {release_group_id}")
    print(f"Release ID: {release_id}")
    print(f"Release IDs Dict: {releaseIDsDict}")
    print(f"Artists IDs Dict: {artistsIDsDict}")