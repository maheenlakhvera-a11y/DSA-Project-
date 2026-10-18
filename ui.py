# =========================================================
#  ui.py  —  ArticleHub
# =========================================================

import os
import json
import time

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QProgressBar, QLabel, QLineEdit, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QButtonGroup,
    QStatusBar, QAbstractItemView, QComboBox, QRadioButton,
    QGroupBox, QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt

from scraper import ScraperThread, TARGET
from algorithms import ALL_ALGOS, ALGO_INFO, run_sort
from multi_sort import multi_level_sort
from searching import linear_search, composite_search
from benchmark import benchmark_all

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

COLUMNS = [
    "arxiv_id", "title", "first_author", "author_count",
    "primary_subject", "subject_count", "pages", "figures",
    "comments", "journal_ref", "year", "month", "title_words",
    "category",
]

COLUMN_LABELS = {
    "arxiv_id": "arXiv ID", "title": "Title", "first_author": "First Author",
    "author_count": "Authors", "primary_subject": "Subject",
    "subject_count": "Subjects #", "pages": "Pages", "figures": "Figures",
    "comments": "Comments", "journal_ref": "Journal Ref",
    "year": "Year", "month": "Month", "title_words": "Title Words",
    "category": "Category",
}

COLORS = {
    "base": "#1e1e2e", "mantle": "#181825", "crust": "#11111b",
    "surface0": "#313244", "surface1": "#45475a", "surface2": "#585b70",
    "overlay0": "#6c7086", "overlay1": "#7f849c",
    "text": "#cdd6f4", "subtext": "#a6adc8",
    "blue": "#89b4fa", "lavender": "#b4befe", "sapphire": "#74c7ec",
    "sky": "#89dceb", "teal": "#94e2d5", "green": "#a6e3a1",
    "yellow": "#f9e2af", "peach": "#fab387", "maroon": "#eba0ac",
    "red": "#f38ba8", "mauve": "#cba6f7", "pink": "#f5c2e7",
}

STYLESHEET = f"""
QWidget {{
    background-color: {COLORS['base']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
}}
QMainWindow {{ background-color: {COLORS['base']}; }}
QFrame#sidebar {{ background-color: {COLORS['mantle']}; border-right: 1px solid {COLORS['surface0']}; }}
QLabel#logo {{ color: {COLORS['mauve']}; font-size: 22px; font-weight: bold; padding: 20px 16px; }}
QPushButton#navBtn {{
    background-color: transparent; color: {COLORS['subtext']}; border: none; border-radius: 10px;
    padding: 12px 16px; text-align: left; font-size: 14px; font-weight: 500; margin: 3px 10px;
}}
QPushButton#navBtn:hover {{ background-color: {COLORS['surface0']}; color: {COLORS['text']}; }}
QPushButton#navBtn:checked {{
    background-color: {COLORS['surface0']}; color: {COLORS['mauve']};
    font-weight: bold; border-left: 3px solid {COLORS['mauve']};
}}
QFrame#card {{ background-color: {COLORS['mantle']}; border: 1px solid {COLORS['surface0']}; border-radius: 14px; }}
QLabel#pageTitle {{ color: {COLORS['text']}; font-size: 26px; font-weight: bold; padding: 4px 0; }}
QLabel#pageSubtitle {{ color: {COLORS['subtext']}; font-size: 13px; }}
QLabel#cardTitle {{ color: {COLORS['lavender']}; font-size: 15px; font-weight: bold; }}
QLabel#badge {{ background-color: {COLORS['surface0']}; color: {COLORS['green']}; border-radius: 10px; padding: 6px 14px; font-weight: bold; font-size: 13px; }}
QLabel#statLabel {{ color: {COLORS['subtext']}; font-size: 12px; font-weight: 600; }}
QLabel#statValue {{ color: {COLORS['text']}; font-size: 24px; font-weight: bold; }}
QPushButton {{
    background-color: {COLORS['surface1']}; color: {COLORS['text']}; border: none;
    border-radius: 10px; padding: 10px 22px; font-weight: 600; font-size: 14px; min-height: 20px;
}}
QPushButton:hover {{ background-color: {COLORS['surface2']}; }}
QPushButton:pressed {{ background-color: {COLORS['overlay0']}; }}
QPushButton:disabled {{ background-color: {COLORS['surface0']}; color: {COLORS['overlay0']}; }}
QPushButton#primary {{ background-color: {COLORS['mauve']}; color: {COLORS['crust']}; }}
QPushButton#primary:hover {{ background-color: {COLORS['lavender']}; }}
QPushButton#success {{ background-color: {COLORS['green']}; color: {COLORS['crust']}; }}
QPushButton#success:hover {{ background-color: {COLORS['teal']}; }}
QPushButton#warning {{ background-color: {COLORS['peach']}; color: {COLORS['crust']}; }}
QPushButton#warning:hover {{ background-color: {COLORS['yellow']}; }}
QPushButton#danger {{ background-color: {COLORS['red']}; color: {COLORS['crust']}; }}
QPushButton#danger:hover {{ background-color: {COLORS['maroon']}; }}
QLineEdit, QComboBox {{
    background-color: {COLORS['surface0']}; border: 2px solid {COLORS['surface0']};
    border-radius: 10px; padding: 9px 14px; color: {COLORS['text']};
    selection-background-color: {COLORS['mauve']}; selection-color: {COLORS['crust']};
}}
QLineEdit:focus, QComboBox:focus {{ border: 2px solid {COLORS['mauve']}; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox QAbstractItemView {{
    background-color: {COLORS['surface0']}; color: {COLORS['text']};
    selection-background-color: {COLORS['mauve']}; selection-color: {COLORS['crust']};
    border: 1px solid {COLORS['surface1']}; border-radius: 8px;
}}
QRadioButton {{ color: {COLORS['text']}; padding: 6px; font-size: 13px; }}
QRadioButton::indicator {{ width: 16px; height: 16px; border-radius: 8px; border: 2px solid {COLORS['surface2']}; background: {COLORS['surface0']}; }}
QRadioButton::indicator:checked {{ background: {COLORS['mauve']}; border: 2px solid {COLORS['mauve']}; }}
QGroupBox {{ color: {COLORS['lavender']}; border: 1px solid {COLORS['surface0']}; border-radius: 10px; margin-top: 12px; padding: 14px; font-weight: bold; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
QProgressBar {{ background-color: {COLORS['surface0']}; border-radius: 10px; text-align: center; color: {COLORS['text']}; font-weight: bold; min-height: 26px; }}
QProgressBar::chunk {{ background-color: {COLORS['mauve']}; border-radius: 10px; }}
QTableWidget {{
    background-color: {COLORS['mantle']}; alternate-background-color: {COLORS['base']};
    gridline-color: {COLORS['surface0']}; border: 1px solid {COLORS['surface0']}; border-radius: 12px;
    color: {COLORS['text']}; selection-background-color: {COLORS['mauve']}; selection-color: {COLORS['crust']}; font-size: 13px;
}}
QHeaderView::section {{ background-color: {COLORS['surface0']}; color: {COLORS['lavender']}; padding: 10px; border: none; border-right: 1px solid {COLORS['mantle']}; font-weight: bold; }}
QHeaderView::section:hover {{ background-color: {COLORS['surface1']}; }}
QTableWidget::item:selected {{ background-color: {COLORS['mauve']}; color: {COLORS['crust']}; }}
QScrollBar:vertical {{ background: {COLORS['mantle']}; width: 12px; border-radius: 6px; margin: 4px; }}
QScrollBar::handle:vertical {{ background: {COLORS['surface1']}; border-radius: 6px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {COLORS['surface2']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar:horizontal {{ background: {COLORS['mantle']}; height: 12px; border-radius: 6px; margin: 4px; }}
QScrollBar::handle:horizontal {{ background: {COLORS['surface1']}; border-radius: 6px; min-width: 30px; }}
QScrollBar::handle:horizontal:hover {{ background: {COLORS['surface2']}; }}
QStatusBar {{ background-color: {COLORS['crust']}; color: {COLORS['subtext']}; border-top: 1px solid {COLORS['surface0']}; padding: 4px 12px; font-size: 12px; }}
"""

def make_stat_card(label, value, color):
    frame = QFrame()
    frame.setObjectName("card")
    frame.setMinimumHeight(100)
    v = QVBoxLayout(frame)
    v.setContentsMargins(20, 16, 20, 16)
    v.setSpacing(6)
    lbl = QLabel(label)
    lbl.setObjectName("statLabel")
    val = QLabel(value)
    val.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
    v.addWidget(lbl)
    v.addWidget(val)
    v.addStretch()
    return {"frame": frame, "value": val}

def fill_table(table, records, columns):
    table.setRowCount(0)
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels([COLUMN_LABELS.get(c, c) for c in columns])
    table.setRowCount(len(records))
    for r, row in enumerate(records):
        for c, key in enumerate(columns):
            val = row.get(key, "")
            item = QTableWidgetItem(str(val))
            if isinstance(val, int): item.setData(Qt.ItemDataRole.DisplayRole, val)
            table.setItem(r, c, item)

class Sidebar(QFrame):
    def __init__(self, on_navigate):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self.on_navigate = on_navigate
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        logo = QLabel("  📚  ArticleHub")
        logo.setObjectName("logo")
        layout.addWidget(logo)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {COLORS['surface0']}; max-height: 1px;")
        layout.addWidget(line)
        layout.addSpacing(16)
        nav_items = [("🔍   Scraper", 0), ("📋   Dataset", 1), ("📊   Sorting", 2), ("🔀   Multi-Sort", 3), ("🔎   Searching", 4), ("⚡   Benchmark", 5)]
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons = []
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.on_navigate(i))
            self.group.addButton(btn, idx)
            self.buttons.append(btn)
            layout.addWidget(btn)
        self.buttons[0].setChecked(True)
        layout.addStretch()
        footer = QLabel("  DSA Project • Fall 2026")
        footer.setStyleSheet(f"color: {COLORS['overlay0']}; padding: 16px; font-size: 11px;")
        layout.addWidget(footer)

class ScraperPage(QWidget):
    def __init__(self, on_data_ready, status_bar):
        super().__init__()
        self.on_data_ready = on_data_ready
        self.status_bar = status_bar
        self.scraper = None
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)
        title = QLabel("Scraper Control Center")
        title.setObjectName("pageTitle")
        sub = QLabel(f"Target: {TARGET:,} articles  •  Category: cs.AI  •  Years: 2019–2024")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(sub)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.card_target    = make_stat_card("🎯  Target",    f"{TARGET:,}", COLORS['mauve'])
        self.card_scraped   = make_stat_card("📥  Scraped",   "0",           COLORS['green'])
        self.card_remaining = make_stat_card("⏳  Remaining", f"{TARGET:,}", COLORS['peach'])
        self.card_status    = make_stat_card("⚡  Status",    "Idle",        COLORS['sky'])
        for c in (self.card_target, self.card_scraped, self.card_remaining, self.card_status):
            stats_row.addWidget(c["frame"])
        layout.addLayout(stats_row)
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)
        url_label = QLabel("🌐  Custom URL  (optional bonus feature)")
        url_label.setObjectName("cardTitle")
        card_layout.addWidget(url_label)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://arxiv.org/list/cs.LG/2023-05  —  leave empty for default scraping")
        self.url_input.setMinimumHeight(44)
        card_layout.addWidget(self.url_input)
        prog_label = QLabel("📈  Progress")
        prog_label.setObjectName("cardTitle")
        card_layout.addWidget(prog_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(TARGET)
        self.progress_bar.setMinimumHeight(28)
        card_layout.addWidget(self.progress_bar)
        info_row = QHBoxLayout()
        self.status_label = QLabel("Ready to start")
        self.status_label.setObjectName("pageSubtitle")
        self.count_label = QLabel(f"0 / {TARGET:,}")
        self.count_label.setObjectName("badge")
        info_row.addWidget(self.status_label, 1)
        info_row.addWidget(self.count_label)
        card_layout.addLayout(info_row)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.start_btn  = QPushButton("▶   Start Scraping")
        self.start_btn.setObjectName("success")
        self.pause_btn  = QPushButton("⏸   Pause")
        self.pause_btn.setObjectName("warning")
        self.resume_btn = QPushButton("⏵   Resume")
        self.resume_btn.setObjectName("primary")
        self.stop_btn   = QPushButton("⏹   Stop")
        self.stop_btn.setObjectName("danger")
        for b in (self.start_btn, self.pause_btn, self.resume_btn, self.stop_btn):
            b.setMinimumHeight(46)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_row.addWidget(b)
        card_layout.addLayout(btn_row)
        layout.addWidget(card)
        layout.addStretch()
        self.start_btn.clicked.connect(self.on_start)
        self.pause_btn.clicked.connect(self.on_pause)
        self.resume_btn.clicked.connect(self.on_resume)
        self.stop_btn.clicked.connect(self.on_stop)
        self.set_buttons(start=True, pause=False, resume=False, stop=False)

    def set_buttons(self, start, pause, resume, stop):
        self.start_btn.setEnabled(start)
        self.pause_btn.setEnabled(pause)
        self.resume_btn.setEnabled(resume)
        self.stop_btn.setEnabled(stop)

    def on_start(self):
        self.progress_bar.setMaximum(TARGET)
        self.progress_bar.setValue(0)
        self.count_label.setText(f"0 / {TARGET:,}")
        self.card_target["value"].setText(f"{TARGET:,}")
        self.card_scraped["value"].setText("0")
        self.card_remaining["value"].setText(f"{TARGET:,}")
        self.on_data_ready([])
        url = self.url_input.text().strip() or None
        self.scraper = ScraperThread(custom_url=url)
        self.scraper.progress.connect(self.on_progress)
        self.scraper.batch_ready.connect(self.on_batch_ready)
        self.scraper.status.connect(self.on_status)
        self.scraper.finished_scraping.connect(self.on_finished)
        self.scraper.incomplete_data.connect(self.on_incomplete_data)
        self.scraper.error_occurred.connect(self.on_error)
        self.scraper.start()
        self.set_buttons(start=False, pause=True, resume=False, stop=True)
        self.card_status["value"].setText("Running")

    def on_pause(self):
        self.scraper.pause()
        self.set_buttons(start=False, pause=False, resume=True, stop=True)
        self.card_status["value"].setText("Paused")

    def on_resume(self):
        self.scraper.resume()
        self.set_buttons(start=False, pause=True, resume=False, stop=True)
        self.card_status["value"].setText("Running")

    def on_stop(self):
        self.status_label.setText("Stopping...")
        self.scraper.stop()
        self.card_status["value"].setText("Stopping")
        self.set_buttons(start=True, pause=False, resume=False, stop=False)

    def on_status(self, msg):
        self.status_label.setText(msg)

    def on_error(self, err_msg):
        self.set_buttons(start=True, pause=False, resume=False, stop=False)
        self.card_status["value"].setText("Error")
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Scraping Error")
        msg.setText("<b>Failed to fetch data</b>")
        msg.setInformativeText(f"Please check the URL format and your internet connection.\n\nError Details: {err_msg}")
        msg.exec()

    def on_progress(self, count):
        self.progress_bar.setMaximum(TARGET)
        self.progress_bar.setValue(min(count, TARGET))
        self.count_label.setText(f"{count:,} / {TARGET:,}")
        self.card_scraped["value"].setText(f"{count:,}")
        self.card_remaining["value"].setText(f"{max(0, TARGET - count):,}")

    def on_batch_ready(self, data):
        self.on_data_ready(data)

    def on_incomplete_data(self, count):
        self.set_buttons(start=True, pause=False, resume=False, stop=False)
        self.card_status["value"].setText("Finished")
        
        self.card_target["value"].setText(f"{count:,}")
        self.card_remaining["value"].setText("0")
        self.progress_bar.setMaximum(max(count, 1))
        self.progress_bar.setValue(count)
        self.count_label.setText(f"{count:,} / {count:,}")
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Scraping Interrupted")
        msg.setText("<b>Data Limit Reached / Stopped</b>")
        msg.setInformativeText(
            f"The scraper has processed <b>{count:,}</b> articles so far.\n\n"
            f"Do you want to SAVE this data and stop?\n"
            f"(Click 'Cancel' to Resume scraping from where it left off)"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {COLORS['base']}; color: {COLORS['text']}; }}
            QLabel {{ color: {COLORS['text']}; }}
            QPushButton {{ background-color: {COLORS['mauve']}; color: {COLORS['crust']}; padding: 8px 20px; border-radius: 6px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background-color: {COLORS['lavender']}; }}
        """)
        
        result = msg.exec()
        if result == QMessageBox.StandardButton.Ok:
            self.on_finished(self.scraper.data)
        else:
            self.status_label.setText("Resuming scraping...")
            self.card_status["value"].setText("Running")
            self.set_buttons(start=False, pause=True, resume=False, stop=True)
            
            new_scraper = ScraperThread(custom_url=self.scraper.custom_url)
            new_scraper.data = self.scraper.data
            new_scraper.seen = self.scraper.seen
            
            self.scraper = new_scraper
            self.scraper.progress.connect(self.on_progress)
            self.scraper.batch_ready.connect(self.on_batch_ready)
            self.scraper.status.connect(self.on_status)
            self.scraper.finished_scraping.connect(self.on_finished)
            self.scraper.incomplete_data.connect(self.on_incomplete_data)
            self.scraper.error_occurred.connect(self.on_error)
            
            self.scraper.start()

    def on_finished(self, data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        self.status_label.setText(f"✅  Completed — {len(data):,} articles saved")
        self.set_buttons(start=True, pause=False, resume=False, stop=False)
        self.card_status["value"].setText("Idle")
        self.status_bar.showMessage(f"Saved {len(data):,} articles to data.json")
        self.on_data_ready(data)

class DatasetPage(QWidget):
    def __init__(self, status_bar, on_load_callback, on_clear_callback):
        super().__init__()
        self.status_bar = status_bar
        self.on_load_callback = on_load_callback
        self.on_clear_callback = on_clear_callback
        self.data = []
        self.filtered = []
        self.build_ui()
        
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)
        title = QLabel("Dataset Viewer")
        title.setObjectName("pageTitle")
        sub = QLabel("Browse all scraped articles. Columns are resizable.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(sub)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.stat_total    = make_stat_card("Total Articles", "0", COLORS['blue'])
        self.stat_filtered = make_stat_card("Showing",        "0", COLORS['green'])
        self.stat_cols     = make_stat_card("Columns",        str(len(COLUMNS)), COLORS['mauve'])
        for c in (self.stat_total, self.stat_filtered, self.stat_cols):
            stats_row.addWidget(c["frame"])
        layout.addLayout(stats_row)
        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.load_btn = QPushButton("📂   Load Saved Data")
        self.load_btn.setObjectName("primary")
        self.load_btn.setMinimumHeight(40)
        self.clear_btn = QPushButton("🗑️   Clear Dataset")
        self.clear_btn.setObjectName("danger")
        self.clear_btn.setMinimumHeight(40)
        action_row.addWidget(self.load_btn)
        action_row.addWidget(self.clear_btn)
        action_row.addStretch()
        layout.addLayout(action_row)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        fill_table(self.table, [], COLUMNS)
        layout.addWidget(self.table, 1)
        self.load_btn.clicked.connect(self.on_load_clicked)
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        
    def set_data(self, data):
        self.data = data
        self.filtered = list(data)
        self.refresh_table()
        
    def refresh_table(self):
        fill_table(self.table, self.filtered, COLUMNS)
        self.stat_total["value"].setText(f"{len(self.data):,}")
        self.stat_filtered["value"].setText(f"{len(self.filtered):,}")
        
    def on_data_updated(self, data):
        self.set_data(data)
        if data:
            self.status_bar.showMessage(f"Dataset updated — {len(data):,} articles")
        else:
            self.status_bar.showMessage("Dataset cleared.")
            
    def on_load_clicked(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.set_data(data)
                self.status_bar.showMessage(f"Loaded {len(data):,} articles from data.json")
                self.on_load_callback(data)
            except Exception as e:
                self.status_bar.showMessage(f"Failed to load: {e}")
        else:
            self.status_bar.showMessage("No saved data found.")
            
    def on_clear_clicked(self):
        self.data = []
        self.filtered = []
        self.refresh_table()
        if os.path.exists(DATA_FILE):
            try: os.remove(DATA_FILE)
            except Exception: pass
        self.status_bar.showMessage("Dataset cleared and data.json removed.")
        self.on_clear_callback() 

class SortingPage(QWidget):
    def __init__(self, get_data, status_bar):
        super().__init__()
        self.get_data = get_data
        self.status_bar = status_bar
        self.search_page = None 
        self.current_result = None
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)
        title = QLabel("Sorting Studio")
        title.setObjectName("pageTitle")
        sub = QLabel("Choose a column and an algorithm, then sort.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(sub)
        
        controls = QFrame()
        controls.setObjectName("card")
        c_layout = QVBoxLayout(controls)
        c_layout.setContentsMargins(24, 24, 24, 24)
        c_layout.setSpacing(16)
        
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        
        col_box = QVBoxLayout()
        col_box.addWidget(QLabel("📋  Column"))
        self.col_combo = QComboBox()
        self.col_combo.addItems([COLUMN_LABELS[c] for c in COLUMNS])
        self.col_combo.setMinimumWidth(220)
        col_box.addWidget(self.col_combo)
        row1.addLayout(col_box)
        
        algo_box = QVBoxLayout()
        algo_box.addWidget(QLabel("⚙️  Algorithm"))
        self.algo_combo = QComboBox()
        for a in ALL_ALGOS:
            info = ALGO_INFO[a]
            tag = "⭐" if info["extra"] else "📘"
            self.algo_combo.addItem(f"{tag}  {a}  ({info['complexity']})")
        self.algo_combo.setMinimumWidth(280)
        algo_box.addWidget(self.algo_combo)
        row1.addLayout(algo_box)
        row1.addStretch()
        c_layout.addLayout(row1)

        scope_box = QGroupBox("Sort Scope")
        s_layout = QHBoxLayout(scope_box)
        self.scope_full = QRadioButton("Full Dataset")
        self.scope_filtered = QRadioButton("Currently Filtered")
        self.scope_full.setChecked(True)
        s_layout.addWidget(self.scope_full)
        s_layout.addWidget(self.scope_filtered)
        s_layout.addStretch()
        c_layout.addWidget(scope_box)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.sort_btn = QPushButton("🔀   Sort Now")
        self.sort_btn.setObjectName("primary")
        self.sort_btn.setMinimumHeight(46)
        self.bench_btn = QPushButton("⚡   Run Benchmark")
        self.bench_btn.setObjectName("warning")
        self.bench_btn.setMinimumHeight(46)
        self.reset_btn = QPushButton("🔄   Reset")
        self.reset_btn.setMinimumHeight(46)
        btn_row.addWidget(self.sort_btn)
        btn_row.addWidget(self.bench_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch()
        c_layout.addLayout(btn_row)
        
        layout.addWidget(controls)

        result_row = QHBoxLayout()
        result_row.setSpacing(16)
        self.card_algo    = make_stat_card("Algorithm",        "—", COLORS['mauve'])
        self.card_time    = make_stat_card("⏱️  Time (ms)",    "—", COLORS['sky'])
        self.card_comps   = make_stat_card("🔍  Comparisons",  "—", COLORS['peach'])
        self.card_swaps   = make_stat_card("🔁  Swaps",        "—", COLORS['green'])
        self.card_complex = make_stat_card("📈  Complexity",   "—", COLORS['lavender'])
        self.card_stable  = make_stat_card("🎯  Stable",       "—", COLORS['pink'])
        for c in (self.card_algo, self.card_time, self.card_comps, self.card_swaps,
                  self.card_complex, self.card_stable):
            result_row.addWidget(c["frame"])
        layout.addLayout(result_row)

        self.result_table = QTableWidget()
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.verticalHeader().setVisible(False)
        fill_table(self.result_table, [], COLUMNS)
        layout.addWidget(self.result_table, 1)

        self.sort_btn.clicked.connect(self.on_sort)
        self.bench_btn.clicked.connect(self.on_benchmark)
        self.reset_btn.clicked.connect(self.on_reset)

    def clear_sorting_state(self):
        self.result_table.setRowCount(0)
        for c in (self.card_algo, self.card_time, self.card_comps, self.card_swaps,
                  self.card_complex, self.card_stable):
            c["value"].setText("—")

    def _get_column_key(self):
        label = self.col_combo.currentText()
        for k, v in COLUMN_LABELS.items():
            if v == label: return k
        return COLUMNS[0]

    def _get_scope_data(self):
        if self.scope_filtered.isChecked():
            if self.search_page and getattr(self.search_page, 'last_results', []):
                return self.search_page.last_results
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("No Filtered Data")
                msg.setText("<b>No filtered data found!</b>")
                msg.setInformativeText("Please go to the 'Search Explorer' tab and apply a search or filter first. Then come back and sort the filtered results.")
                msg.exec()
                self.scope_full.setChecked(True)
                return []
        return self.get_data()

    def on_sort(self):
        data = self._get_scope_data()
        if not data:
            if not self.scope_filtered.isChecked():
                self.status_bar.showMessage("No data to sort!")
            return

        col = self._get_column_key()
        algo_text = self.algo_combo.currentText()
        algo = algo_text.split("  ")[1].strip()
        sample = data[:1000] if len(data) > 1000 else data

        sorted_data, t_ms, comps, swaps = run_sort(algo, sample, col)
        self.current_result = sorted_data

        info = ALGO_INFO[algo]
        self.card_algo["value"].setText(algo)
        self.card_time["value"].setText(f"{t_ms:.2f}")
        self.card_comps["value"].setText(f"{comps:,}")
        self.card_swaps["value"].setText(f"{swaps:,}")
        self.card_complex["value"].setText(info["complexity"])
        self.card_stable["value"].setText("Yes" if info["stable"] else "No")

        fill_table(self.result_table, sorted_data, COLUMNS)
        self.status_bar.showMessage(f"Sorted {len(sample):,} records using {algo} in {t_ms:.2f} ms")

    def on_benchmark(self):
        data = self._get_scope_data()
        if not data: return
        
        main_window = self.window()
        main_window.navigate(5)
        bench_page = main_window.stack.widget(5)
        bench_page.run(data, self._get_column_key())

    def on_reset(self):
        data = self.get_data()
        fill_table(self.result_table, data, COLUMNS)
        for c in (self.card_algo, self.card_time, self.card_comps, self.card_swaps,
                  self.card_complex, self.card_stable):
            c["value"].setText("—")

class MultiLevelPage(QWidget):
    def __init__(self, get_data, status_bar):
        super().__init__()
        self.get_data = get_data
        self.status_bar = status_bar
        self.levels = []
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)
        
        title = QLabel("Multi-Level Sorting")
        title.setObjectName("pageTitle")
        sub = QLabel("Sort by multiple columns in priority order. (Merge Sort is used for stability).")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(sub)

        self.levels_frame = QFrame()
        self.levels_frame.setObjectName("card")
        self.levels_frame.setMaximumHeight(280)
        
        frame_layout = QVBoxLayout(self.levels_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        self.levels_layout = QVBoxLayout(scroll_content)
        self.levels_layout.setContentsMargins(10, 5, 10, 5)
        self.levels_layout.setSpacing(10)
        self.levels_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(scroll_content)
        frame_layout.addWidget(scroll)
        layout.addWidget(self.levels_frame)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.add_btn = QPushButton("➕   Add Sort Level")
        self.add_btn.setObjectName("success")
        self.add_btn.setMinimumHeight(44)
        self.remove_btn = QPushButton("➖   Remove Last Level")
        self.remove_btn.setObjectName("warning")
        self.remove_btn.setMinimumHeight(44)
        self.apply_btn = QPushButton("🔀   Apply Multi-Level Sort")
        self.apply_btn.setObjectName("primary")
        self.apply_btn.setMinimumHeight(44)
        self.reset_btn = QPushButton("🔄   Reset")
        self.reset_btn.setMinimumHeight(44)
        
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.remove_btn)
        btn_row.addWidget(self.apply_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        stats_row = QHBoxLayout()
        self.card_levels = make_stat_card("Active Levels", "0", COLORS['mauve'])
        self.card_time   = make_stat_card("⏱️  Time (ms)", "—", COLORS['sky'])
        self.card_rows   = make_stat_card("📋  Rows Sorted", "0", COLORS['green'])
        stats_row.addWidget(self.card_levels["frame"])
        stats_row.addWidget(self.card_time["frame"])
        stats_row.addWidget(self.card_rows["frame"])
        stats_row.addStretch()
        layout.addLayout(stats_row)

        self.result_table = QTableWidget()
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.verticalHeader().setVisible(False)
        fill_table(self.result_table, [], COLUMNS)
        layout.addWidget(self.result_table, 1)

        self.add_btn.clicked.connect(self.add_level)
        self.remove_btn.clicked.connect(self.remove_level)
        self.apply_btn.clicked.connect(self.apply_sort)
        self.reset_btn.clicked.connect(self.reset_table)
        self.add_level()

    def add_level(self):
        level_num = len(self.levels) + 1
        row = QWidget()
        row.setStyleSheet(f"background-color: {COLORS['surface0']}; border-radius: 10px; padding: 4px;")
        r_layout = QHBoxLayout(row)
        r_layout.setContentsMargins(12, 8, 12, 8)
        r_layout.setSpacing(10)
        
        badge = QLabel(f"Level {level_num}")
        badge.setStyleSheet(f"color: {COLORS['mauve']}; font-weight: bold; min-width: 70px;")
        
        col_combo = QComboBox()
        col_combo.addItems([COLUMN_LABELS[c] for c in COLUMNS])
        col_combo.setMinimumWidth(240)
        
        order_combo = QComboBox()
        order_combo.addItems(["Ascending ⬆", "Descending ⬇"])
        order_combo.setMinimumWidth(160)
        
        r_layout.addWidget(badge)
        r_layout.addWidget(QLabel("Column:"))
        r_layout.addWidget(col_combo)
        r_layout.addWidget(QLabel("Order:"))
        r_layout.addWidget(order_combo)
        r_layout.addStretch()
        
        self.levels_layout.addWidget(row)
        self.levels.append({"widget": row, "badge": badge, "col": col_combo, "order": order_combo})
        self.card_levels["value"].setText(str(len(self.levels)))

    def remove_level(self):
        if not self.levels: return
        level = self.levels.pop()
        level["widget"].deleteLater()
        self.card_levels["value"].setText(str(len(self.levels)))

    def _get_column_key(self, label):
        for k, v in COLUMN_LABELS.items():
            if v == label: return k
        return COLUMNS[0]

    def apply_sort(self):
        data = self.get_data()
        if not data:
            self.status_bar.showMessage("No data available to sort.")
            return
        if not self.levels:
            self.status_bar.showMessage("Add at least one sort level.")
            return
            
        columns_with_order = []
        for lvl in self.levels:
            col_label = lvl["col"].currentText()
            col_key = self._get_column_key(col_label)
            asc = lvl["order"].currentText().startswith("Ascending")
            columns_with_order.append((col_key, asc))
            
        t0 = time.perf_counter()
        sorted_data = multi_level_sort(data, columns_with_order)
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000
        
        fill_table(self.result_table, sorted_data, COLUMNS)
        self.card_time["value"].setText(f"{elapsed_ms:.2f}")
        self.card_rows["value"].setText(f"{len(sorted_data):,}")
        self.status_bar.showMessage(f"Multi-level sort applied on {len(columns_with_order)} level(s) — {elapsed_ms:.2f} ms")

    def reset_table(self):
        data = self.get_data()
        fill_table(self.result_table, data, COLUMNS)
        self.card_time["value"].setText("—")
        self.card_rows["value"].setText(f"{len(data):,}")
        
    def clear_sorting_state(self):
        self.result_table.setRowCount(0)
        self.card_time["value"].setText("—")
        self.card_rows["value"].setText("0")

class SearchingPage(QWidget):
    def __init__(self, get_data, status_bar):
        super().__init__()
        self.get_data = get_data
        self.status_bar = status_bar
        self.conditions = []
        self.last_results = [] 
        self.build_ui()
        
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(12) # Thoda kam kiya

        title = QLabel("Search Explorer")
        title.setObjectName("pageTitle")
        sub = QLabel("Search by column with advanced filters. Combine with AND / OR / NOT.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(sub)

        # ---- Simple Search Box ----
        card = QFrame()
        card.setObjectName("card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        col_box = QVBoxLayout()
        col_box.addWidget(QLabel("📋  Column"))
        self.col_combo = QComboBox()
        self.col_combo.addItems([COLUMN_LABELS[c] for c in COLUMNS])
        col_box.addWidget(self.col_combo)
        row1.addLayout(col_box)
        
        mode_box = QVBoxLayout()
        mode_box.addWidget(QLabel("🎯  Match Mode"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["contains", "equals", "starts with", "ends with", "greater than", "less than"])
        mode_box.addWidget(self.mode_combo)
        row1.addLayout(mode_box)
        
        query_box = QVBoxLayout()
        query_box.addWidget(QLabel("🔎  Query"))
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Type to search...")
        query_box.addWidget(self.query_input)
        row1.addLayout(query_box, 1) # Query box ko stretch kiya
        
        c_layout.addLayout(row1)
        
        btn_row = QHBoxLayout()
        self.search_btn = QPushButton("🔍   Search")
        self.search_btn.setObjectName("primary")
        self.clear_btn = QPushButton("🔄   Clear")
        btn_row.addWidget(self.search_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        c_layout.addLayout(btn_row)
        
        layout.addWidget(card)

        # ---- Composite Search ----
        comp_group = QGroupBox("Composite Search  (AND / OR / NOT)")
        comp_group.setMaximumHeight(200) # Fix height taake table ko space mile
        comp_layout = QVBoxLayout(comp_group)
        
        # Scroll Area for conditions
        self.cond_scroll = QScrollArea()
        self.cond_scroll.setWidgetResizable(True)
        self.cond_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QWidget()
        self.conditions_container = QVBoxLayout(scroll_widget)
        self.conditions_container.setContentsMargins(0, 0, 0, 0)
        self.conditions_container.setSpacing(8)
        self.cond_scroll.setWidget(scroll_widget)
        
        comp_layout.addWidget(self.cond_scroll)
        
        add_row = QHBoxLayout()
        self.add_cond_btn = QPushButton("➕  Add Condition")
        self.add_cond_btn.setObjectName("success")
        self.run_comp_btn = QPushButton("▶  Run Composite")
        self.run_comp_btn.setObjectName("primary")
        add_row.addWidget(self.add_cond_btn)
        add_row.addWidget(self.run_comp_btn)
        add_row.addStretch()
        comp_layout.addLayout(add_row)
        
        layout.addWidget(comp_group)

        # ---- Stats Row (Compact) ----
        stats_row = QHBoxLayout()
        self.stat_results = make_stat_card("Results", "0", COLORS['green'])
        self.stat_results["frame"].setFixedHeight(80) # Chota card
        stats_row.addWidget(self.stat_results["frame"])
        stats_row.addStretch()
        layout.addLayout(stats_row)

        # ---- Table (Takes remaining space) ----
        self.result_table = QTableWidget()
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.verticalHeader().setVisible(False)
        fill_table(self.result_table, [], COLUMNS)
        layout.addWidget(self.result_table, 1) # Stretch 1

        self.search_btn.clicked.connect(self.on_search)
        self.clear_btn.clicked.connect(self.on_clear)
        self.add_cond_btn.clicked.connect(self.add_condition)
        self.run_comp_btn.clicked.connect(self.on_composite)
        
    def clear_search_state(self):
        self.last_results = []
        self.result_table.setRowCount(0)
        self.stat_results["value"].setText("0")
        
    def _get_column_key(self):
        label = self.col_combo.currentText()
        for k, v in COLUMN_LABELS.items():
            if v == label: return k
        return COLUMNS[0]
        
    def on_search(self):
        data = self.get_data()
        if not data:
            self.status_bar.showMessage("No data. Scrape first.")
            return
            
        col = self._get_column_key()
        query = self.query_input.text().strip().lower()
        mode = self.mode_combo.currentText()
        
        results = linear_search(data, col, query, mode)
        self.last_results = results
        fill_table(self.result_table, results, COLUMNS)
        self.stat_results["value"].setText(f"{len(results):,}")
        self.status_bar.showMessage(f"Found {len(results):,} results")
        
    def on_clear(self):
        self.query_input.clear()
        data = self.get_data()
        self.last_results = []
        fill_table(self.result_table, data, COLUMNS)
        self.stat_results["value"].setText(f"{len(data):,}")
        
    def add_condition(self):
        row = QWidget()
        r_layout = QHBoxLayout(row)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(8)
        logic = QComboBox()
        logic.addItems(["AND", "OR", "NOT"])
        logic.setFixedWidth(90)
        col = QComboBox()
        col.addItems([COLUMN_LABELS[c] for c in COLUMNS])
        col.setFixedWidth(180)
        mode = QComboBox()
        mode.addItems(["contains", "equals", "starts with", "ends with", "greater than", "less than"])
        mode.setFixedWidth(150)
        q = QLineEdit()
        q.setPlaceholderText("value")
        remove = QPushButton("✖")
        remove.setObjectName("danger")
        remove.setFixedWidth(40)
        r_layout.addWidget(logic)
        r_layout.addWidget(col)
        r_layout.addWidget(mode)
        r_layout.addWidget(q, 1)
        r_layout.addWidget(remove)
        cond = {"widget": row, "logic": logic, "col": col, "mode": mode, "query": q}
        self.conditions.append(cond)
        self.conditions_container.addWidget(row)
        remove.clicked.connect(lambda: self._remove_condition(cond))
        
    def _remove_condition(self, cond):
        if cond in self.conditions:
            self.conditions.remove(cond)
            cond["widget"].deleteLater()
            
    def on_composite(self):
        data = self.get_data()
        if not data or not self.conditions: return
        cond_list = []
        for c in self.conditions:
            label = c["col"].currentText()
            key = None
            for k, v in COLUMN_LABELS.items():
                if v == label:
                    key = k
                    break
            cond_list.append({"column": key or COLUMNS[0], "query": c["query"].text().strip(), "mode": c["mode"].currentText(), "logic": c["logic"].currentText()})
        
        results = composite_search(data, cond_list)
        self.last_results = results
        fill_table(self.result_table, results, COLUMNS)
        self.stat_results["value"].setText(f"{len(results):,}")
        self.status_bar.showMessage(f"Composite search: {len(results):,} results")

class BenchmarkPage(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.build_ui()
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)
        title = QLabel("Benchmark Arena")
        title.setObjectName("pageTitle")
        sub = QLabel("Run all sorting algorithms on the same column and compare.")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(sub)
        info = QLabel("ℹ️  Benchmark runs on 1000 records for fair comparison (slow algorithms on 15k are impractical).")
        info.setObjectName("pageSubtitle")
        layout.addWidget(info)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Algorithm", "Time (ms)", "Comparisons", "Swaps", "Complexity", "Stable", "Type"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)
    def run(self, data, column):
        if not data:
            self.status_bar.showMessage("No data to benchmark!")
            return
        sample = data[:1000] if len(data) > 1000 else data
        self.status_bar.showMessage(f"Running benchmark on {len(sample):,} records — column: {column}")
        results = benchmark_all(sample, column)
        self.table.setRowCount(len(results))
        for r, row in enumerate(results):
            self.table.setItem(r, 0, QTableWidgetItem(row["algorithm"]))
            self.table.setItem(r, 1, QTableWidgetItem(f"{row['time_ms']:.2f}"))
            self.table.setItem(r, 2, QTableWidgetItem(f"{row['comparisons']:,}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{row['swaps']:,}"))
            self.table.setItem(r, 4, QTableWidgetItem(row["complexity"]))
            self.table.setItem(r, 5, QTableWidgetItem(row["stable"]))
            self.table.setItem(r, 6, QTableWidgetItem(row["type"]))
        self.status_bar.showMessage(f"Benchmark complete — {len(results)} algorithms tested")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArticleHub — Research Articles Manager")
        self.setStyleSheet(STYLESHEET)
        self.setStatusBar(QStatusBar())
        self.status_bar_message = "Ready"
        self.statusBar().showMessage(self.status_bar_message)
        self._data = []
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.sidebar = Sidebar(on_navigate=self.navigate)
        root.addWidget(self.sidebar)
        self.stack = QStackedWidget()
        
        self.dataset_page    = DatasetPage(
            status_bar=self.statusBar(), 
            on_load_callback=self._on_data, 
            on_clear_callback=self._on_dataset_cleared
        )
        self.search_page     = SearchingPage(get_data=self._get_data, status_bar=self.statusBar())
        self.sorting_page    = SortingPage(get_data=self._get_data, status_bar=self.statusBar())
        self.sorting_page.search_page = self.search_page
        self.scraper_page    = ScraperPage(on_data_ready=self._on_data, status_bar=self.statusBar())
        self.multilevel_page = MultiLevelPage(get_data=self._get_data, status_bar=self.statusBar())
        self.bench_page      = BenchmarkPage(status_bar=self.statusBar())
        
        self.stack.addWidget(self.scraper_page)
        self.stack.addWidget(self.dataset_page)
        self.stack.addWidget(self.sorting_page)
        self.stack.addWidget(self.multilevel_page)
        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.bench_page)
        root.addWidget(self.stack, 1)
        self.setCentralWidget(central)
        self.showMaximized()
        
    def _get_data(self):
        return self._data
        
    def _on_data(self, data):
        self._data = data
        self.dataset_page.on_data_updated(data)
        
    def _on_dataset_cleared(self):
        self._data = []
        self.sorting_page.clear_sorting_state()
        self.multilevel_page.clear_sorting_state()
        self.search_page.clear_search_state()
        
    def navigate(self, idx):
        self.stack.setCurrentIndex(idx)
        
    def closeEvent(self, event):
        if self.scraper_page.scraper is not None and self.scraper_page.scraper.isRunning():
            self.scraper_page.scraper.stop()
            self.scraper_page.scraper.wait()
        event.accept()