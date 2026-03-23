import sys
import prepareDataToImport
import re
import sqlite3
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHBoxLayout, QHeaderView, QFileDialog, QMessageBox,
                             QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont

import appleScripting
from dbManager import parseLibraryXMLtoSQL
import apiToDb

if getattr(sys, 'frozen', False):
    BASE_DIR = Path.home() / "AppleMusicManager"
else:
    BASE_DIR = Path(__file__).parent.absolute()

DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "main.db"


def ensure_library_table():
    if not DATABASE_PATH.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT 1 FROM Library LIMIT 1')
        except sqlite3.OperationalError:
            print("Table 'Library' missing or empty. Parsing XML...")

            xml_path = DATA_DIR / "library.xml"
            parseLibraryXMLtoSQL(xml_path=str(xml_path), db_path=str(DATABASE_PATH))


def get_metadata_from_db():
    if not DATABASE_PATH.exists():
        return []

    ensure_library_table()

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            sql_query = """
            SELECT 
                L.Title,
                L.Album,
                L.Artist,
                COALESCE(GROUP_CONCAT(DISTINCT G.genre_name), 'Unknown') AS Genres,
                COALESCE(GROUP_CONCAT(DISTINCT I.instrument_name), 'None') AS Instruments
            FROM Library L
            LEFT JOIN TrackDetails TD ON L.ID = TD.track_id
            LEFT JOIN ReleaseGroup RG ON TD.release_group_id = RG.release_group_id
            LEFT JOIN ReleaseGroupGenres RGG ON RG.release_group_id = RGG.release_group_id
            LEFT JOIN Genres G ON RGG.genre_id = G.genre_id
            LEFT JOIN TrackInstruments TI ON L.ID = TI.track_id
            LEFT JOIN Instruments I ON TI.instrument_id = I.instrument_id
            GROUP BY L.ID
            ORDER BY L.Title, L.Album;
            """
            cursor.execute(sql_query)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error during fetch: {e}")
        return []




class WorkerThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, db_path, user_email):
        super().__init__()
        self.db_path = str(db_path)
        self.user_email = user_email

    def run(self):
        pd = apiToDb.PopulateDatabase(self.db_path, userEmail=self.user_email)
        pd.populatePart1()
        pd.populateGenres()
        self.finished_signal.emit()




class AppleMusicPushThread(QThread):
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, db_path):
        super().__init__()
        self.db_path = str(db_path)

    def run(self):
        try:
            importData = prepareDataToImport.ImportDataToLibraryTable(self.db_path)
            importData.importInstrumentsToLibrary()
            importData.importSubgenresToLibrary()
            appleScripting.exportDataToAppleMusic(self.db_path)
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.finished_signal.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apple Music Metadata Manager")
        self.setGeometry(100, 100, 1200, 700)
        self.apply_stylesheet()

        self.email_address = None
        self.worker = None
        self.prepare_worker = None
        self.push_worker = None

        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setCentralWidget(widget)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)

        email_layout = QHBoxLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email for API...")

        self.submit_email_btn = QPushButton("Submit Email")
        self.submit_email_btn.setObjectName("accentButton")
        self.submit_email_btn.clicked.connect(self.submit_email)

        email_layout.addWidget(self.email_input)
        email_layout.addWidget(self.submit_email_btn)
        button_layout.addLayout(email_layout)

        self.btn_import_xml = QPushButton("1. Import Library (XML)")
        self.btn_import_xml.clicked.connect(self.import_library)

        self.btn_get_cloud = QPushButton("2. Get Data from Cloud")
        self.btn_get_cloud.clicked.connect(self.get_data)


        self.btn_push_apple = QPushButton("3. Push Metadata to Apple Music")
        self.btn_push_apple.setObjectName("accentButton")
        self.btn_push_apple.clicked.connect(self.import_metadata)

        self.btn_stop_cloud = QPushButton("Stop Cloud Sync")
        self.btn_stop_cloud.setEnabled(False)
        self.btn_stop_cloud.clicked.connect(self.stop_data)

        self.btn_refresh = QPushButton("Refresh Table View")
        self.btn_refresh.clicked.connect(self.refresh_data)

        self.btn_delete_db = QPushButton("Delete Database (Reset)")
        self.btn_delete_db.setObjectName("dangerButton")
        self.btn_delete_db.clicked.connect(self.delete_database)

        button_layout.addWidget(self.btn_import_xml)
        button_layout.addWidget(self.btn_get_cloud)
        button_layout.addWidget(self.btn_push_apple)
        button_layout.addWidget(self.btn_stop_cloud)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_delete_db)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title", "Album", "Artist", "Genres", "Instruments"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        main_layout.addLayout(button_layout, 1)
        main_layout.addWidget(self.table, 4)

        self.refresh_data()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f0f4f8; 
                color: #1e293b; 
                font-family: 'Segoe UI', 'San Francisco', sans-serif;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 12px;
                color: #1e293b;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6; 
            }

            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
                color: #334155;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border: 1px solid #94a3b8;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
            QPushButton:disabled {
                background-color: #f1f5f9;
                color: #94a3b8;
                border: 1px solid #e2e8f0;
            }

            QPushButton#accentButton {
                background-color: #3b82f6; 
                color: #ffffff;
                border: none;
            }
            QPushButton#accentButton:hover {
                background-color: #2563eb; 
            }
            QPushButton#accentButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#accentButton:disabled {
                background-color: #93c5fd;
                color: #eff6ff;
            }

            QPushButton#dangerButton {
                background-color: #ef4444; 
                color: #ffffff;
                border: none;
            }
            QPushButton#dangerButton:hover {
                background-color: #dc2626;
            }
            QPushButton#dangerButton:pressed {
                background-color: #b91c1c;
            }

            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8fafc; 
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                outline: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe; 
                color: #1e40af; 
            }

            QHeaderView::section {
                background-color: #e2e8f0;
                color: #475569;
                padding: 8px;
                border: none;
                border-right: 1px solid #cbd5e1;
                border-bottom: 1px solid #cbd5e1;
                font-weight: bold;
            }

            QScrollBar:vertical {
                border: none;
                background-color: #f0f4f8;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def submit_email(self):
        email = self.email_input.text().strip()
        if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            self.email_address = email
            QMessageBox.information(self, "Success", f"Email set to: {email}")
        else:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")

    def refresh_data(self):
        data = get_metadata_from_db()
        data.sort(key=lambda row: 0 if (row[3] != 'Unknown' or row[4] != 'None') else 1)

        self.table.setRowCount(0)
        self.table.setRowCount(len(data))

        analyzed_color = QColor("#dcfce7")

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                display_text = str(col_data).replace(",", ", ")
                item = QTableWidgetItem(display_text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                if col_idx == 3 and col_data != 'Unknown':
                    item.setBackground(analyzed_color)
                elif col_idx == 4 and col_data != 'None':
                    item.setBackground(analyzed_color)

                self.table.setItem(row_idx, col_idx, item)

    def import_library(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        file_path_str, _ = QFileDialog.getOpenFileName(
            self, "Select iTunes/Music XML", "", "XML Files (*.xml)"
        )

        if file_path_str:
            try:
                xml_dest = DATA_DIR / "library.xml"
                shutil.copy2(file_path_str, xml_dest)

                parseLibraryXMLtoSQL(xml_path=str(xml_dest), db_path=str(DATABASE_PATH))

                self.refresh_data()
                QMessageBox.information(self, "Success", "Library imported!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Import failed: {e}")

    def get_data(self):
        if not self.email_address:
            QMessageBox.warning(self, "Required", "Please submit an email address first.")
            return

        self.btn_get_cloud.setEnabled(False)
        self.btn_stop_cloud.setEnabled(True)

        self.worker = WorkerThread(DATABASE_PATH, self.email_address)
        self.worker.finished_signal.connect(self.on_data_finished)
        self.worker.start()

    def stop_data(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.on_data_finished()
            QMessageBox.information(self, "Stopped", "Process terminated.")

    def on_data_finished(self):
        self.btn_get_cloud.setEnabled(True)
        self.btn_stop_cloud.setEnabled(False)
        self.refresh_data()

    def import_metadata(self):
        if not DATABASE_PATH.exists():
            QMessageBox.warning(self, "Error", "Database not found.")
            return

        self.btn_push_apple.setEnabled(False)
        self.btn_push_apple.setText("Pushing to Apple Music... Please wait.")

        self.push_worker = AppleMusicPushThread(DATABASE_PATH)
        self.push_worker.finished_signal.connect(self.on_push_finished)
        self.push_worker.error_signal.connect(self.on_push_error)
        self.push_worker.start()

    def on_push_finished(self):
        self.btn_push_apple.setEnabled(True)
        self.btn_push_apple.setText("4. Push Metadata to Apple Music")
        QMessageBox.information(self, "Success", "Metadata sync complete.")

    def on_push_error(self, error_msg):
        self.btn_push_apple.setEnabled(True)
        self.btn_push_apple.setText("4. Push Metadata to Apple Music")
        QMessageBox.critical(self, "AppleScript Error", f"Failed to sync metadata:\n{error_msg}")

    def delete_database(self):
        confirm = QMessageBox.question(self, "Confirm", "Delete main.db? This resets all data.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            DATABASE_PATH.unlink(missing_ok=True)
            self.refresh_data()
            QMessageBox.information(self, "Deleted", "Database removed.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())