import sqlite3
import xml.etree.ElementTree as ET
import os
import sys  
from time import sleep
import getFromAPI


if getattr(sys, 'frozen', False):
    SCRIPT_DIR = sys._MEIPASS
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def parseLibraryXMLtoSQL(xml_path, db_path):

    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Erro: Arquivo XML não encontrado em {xml_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql_path = os.path.join(SCRIPT_DIR, 'create_tables.sql')
    with open(sql_path, 'r') as file:
        sql_script = file.read()
    cursor.executescript(sql_script)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    tracks_dict = None
    for dict_item in root.iter('dict'):
        for key in dict_item.iter('key'):
            if key.text == 'Tracks':
                tracks_dict = next(dict_item.iter('dict'))
                break
        if tracks_dict is not None:
            break

    if tracks_dict is not None:
        for track in tracks_dict.iter('dict'):
            track_name = None
            album_name = None
            artist_name = None
            persistent_id_value = None

            for i, child in enumerate(track):
                if child.tag == 'key':
                    if child.text == 'Name':
                        track_name = track[i + 1].text
                    elif child.text == 'Album':
                        album_name = track[i + 1].text
                    elif child.text == 'Artist':
                        artist_name = track[i + 1].text
                    elif child.text == 'Persistent ID':
                        persistent_id_value = track[i + 1].text

            if track_name and album_name and artist_name and persistent_id_value:
                cursor.execute('''
                INSERT OR IGNORE INTO library (Title, Album, Artist, persistent_id)
                VALUES (?, ?, ?, ?)
                ''', (track_name, album_name, artist_name, persistent_id_value))

        conn.commit()
        conn.close()

if __name__ == '__main__':
    print()

    parseLibraryXMLtoSQL()