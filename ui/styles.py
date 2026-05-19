APP_STYLE = """
* {
    font-family: "Segoe UI", "Arial";
    font-size: 12px;
    color: #1f2933;
}

QMainWindow {
    background: #eef1f4;
}

QFrame#Sidebar {
    background: #2f3742;
    border-right: 1px solid #1f2730;
}

QFrame#Sidebar QLabel {
    color: #e7edf3;
}

QFrame#Sidebar QLabel#Muted {
    color: #aeb8c3;
}

QFrame#Sidebar QFrame#UserCard {
    background: #38424e;
    border: 1px solid #4a5563;
    border-radius: 4px;
}

QFrame#UserCard,
QFrame#MetricCard,
QFrame#InfoCard,
QFrame#TransportCard,
QFrame#OrderCard,
QFrame#HeaderStat {
    background: #fdfefe;
    border: 1px solid #c8d0d8;
    border-radius: 4px;
}

QLabel#LogoText {
    color: #31506f;
    font-size: 12px;
    font-weight: 700;
}

QLabel#AppTitle {
    font-size: 19px;
    font-weight: 700;
    color: #1e2a36;
}

QLabel#PageTitle {
    font-size: 17px;
    font-weight: 700;
    color: #1f2933;
}

QLabel#SectionTitle {
    font-size: 13px;
    font-weight: 700;
}

QLabel#Muted {
    color: #66727f;
}

QLabel#MetricValue {
    font-size: 21px;
    font-weight: 800;
    color: #25313d;
}

QLabel#MetricTitle {
    color: #42505d;
    font-weight: 600;
}

QLabel#StatusPill {
    padding: 3px 8px;
    border-radius: 4px;
    background: #e4e9ef;
    border: 1px solid #c5cdd6;
    color: #334155;
    font-weight: 700;
}

QPushButton {
    background: #3f6288;
    color: #ffffff;
    border: 1px solid #355574;
    border-radius: 4px;
    padding: 5px 10px;
    min-height: 22px;
    font-weight: 600;
}

QPushButton:hover {
    background: #4b6e94;
    border-color: #3b5d7f;
}

QPushButton:pressed {
    background: #304d6d;
}

QPushButton#NavButton {
    background: transparent;
    color: #d8e0e8;
    text-align: left;
    padding: 8px 12px;
    border: 1px solid transparent;
    border-radius: 3px;
    font-weight: 600;
}

QPushButton#NavButton:hover {
    background: #394553;
    color: #ffffff;
    border-color: #4a5969;
}

QPushButton#NavButton[active="true"] {
    background: #51606f;
    color: #ffffff;
    border-color: #738193;
}

QPushButton#SecondaryButton {
    background: #e6eaee;
    color: #23313f;
    border: 1px solid #b9c2cb;
}

QPushButton#SecondaryButton:hover {
    background: #d8dee5;
}

QGroupBox {
    background: #fdfefe;
    border: 1px solid #c8d0d8;
    border-radius: 4px;
    margin-top: 14px;
    padding: 14px 8px 8px 8px;
    font-weight: 700;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 9px;
    padding: 0 4px;
    color: #26323f;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #f5f7f9;
    border: 1px solid #aeb8c3;
    border-radius: 3px;
    gridline-color: #d5dce3;
    selection-background-color: #c9d8e7;
    selection-color: #111827;
}

QTableWidget::item {
    padding: 2px 5px;
}

QHeaderView::section {
    background: #dfe5eb;
    color: #24313f;
    padding: 5px 6px;
    border: none;
    border-right: 1px solid #c4ccd5;
    border-bottom: 1px solid #aeb8c3;
    font-weight: 700;
}

QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background: #ffffff;
    border: 1px solid #aeb8c3;
    border-radius: 4px;
    padding: 5px 7px;
    min-height: 22px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 1px solid #3f6288;
}

QRadioButton {
    spacing: 5px;
    font-weight: 600;
    color: #25313d;
}

QProgressBar {
    border: 1px solid #aeb8c3;
    border-radius: 3px;
    background: #eef1f4;
    color: #1f2933;
    font-weight: 700;
    text-align: center;
}

QProgressBar::chunk {
    background: #b9dfc2;
}

QListWidget {
    background: #ffffff;
    border: 1px solid #aeb8c3;
    border-radius: 3px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: #e1e6eb;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #aeb8c3;
    border-radius: 3px;
}

QFrame#Sidebar QLabel#Muted {
    color: #aeb8c3;
}
"""
