import os

from PyQt6.QtWidgets import QFileDialog, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QWidget

from data import mock_data
from services.pdf_report_service import PDFReportService
from services.settings_service import settings_service
from ui.components import group_box, make_table, page_shell, refill_table, title_label


class ReportsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.pdf_service = PDFReportService()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Отчёты"))

        folder_box, folder_layout = group_box("Папка сохранения отчётов")
        folder_row = QWidget()
        folder_row_layout = QHBoxLayout(folder_row)
        folder_row_layout.setContentsMargins(0, 0, 0, 0)
        self.reports_dir_label = QLabel(str(settings_service.get_reports_dir()))
        self.reports_dir_label.setWordWrap(True)
        select_folder_button = QPushButton("Выбрать папку")
        reset_folder_button = QPushButton("По умолчанию")
        select_folder_button.clicked.connect(self._select_reports_folder)
        reset_folder_button.clicked.connect(self._reset_reports_folder)
        folder_row_layout.addWidget(self.reports_dir_label, 1)
        folder_row_layout.addWidget(select_folder_button)
        folder_row_layout.addWidget(reset_folder_button)
        folder_layout.addWidget(folder_row)
        layout.addWidget(folder_box)

        actions_box, actions_layout = group_box("Генерация PDF")
        actions_row = QWidget()
        row_layout = QHBoxLayout(actions_row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        buttons = [
            ("Суточная сводка", self._daily_summary),
            ("Отчёт по отгрузкам", self._shipment_report),
            ("Акт расхождений", self._discrepancy_report),
            ("Паспорт партии", self._batch_passport),
            ("Открыть папку reports", self._open_reports_folder),
        ]
        for title, handler in buttons:
            button = QPushButton(title)
            button.clicked.connect(handler)
            row_layout.addWidget(button)
        row_layout.addStretch(1)
        actions_layout.addWidget(actions_row)
        layout.addWidget(actions_box)

        reports_box, reports_layout = group_box("Список сформированных PDF")
        self.reports_table = make_table(["Тип отчёта", "Дата формирования", "Пользователь", "Путь к файлу"], mock_data.REPORTS, min_height=300)
        reports_layout.addWidget(self.reports_table)
        layout.addWidget(reports_box)
        layout.addStretch(1)

    def _daily_summary(self) -> None:
        path = self.pdf_service.generate_daily_summary_report()
        self._after_generate(path)

    def _shipment_report(self) -> None:
        shipment_id = "SHP-7102"
        path = self.pdf_service.generate_shipment_report(
            {
                "id": shipment_id,
                "status": mock_data.SHIPMENT_STATUSES[shipment_id],
                "recipient": mock_data.SHIPMENT_INFO[shipment_id]["Маршрут"],
                "weight": "5 900 кг",
                "packages": str(len(mock_data.SHIPMENT_ITEMS[shipment_id])),
                "onec_status": mock_data.ONEC_SYNC_STATUS[shipment_id],
            }
        )
        self._after_generate(path)

    def _discrepancy_report(self) -> None:
        if not mock_data.PROBLEM_POSITIONS:
            QMessageBox.warning(self, "PDF", "Нет расхождений для отчёта.")
            return
        path = self.pdf_service.generate_discrepancy_report(mock_data.PROBLEM_POSITIONS[0])
        self._after_generate(path)

    def _batch_passport(self) -> None:
        path = self.pdf_service.generate_batch_passport({"id": "SUP-4301"})
        self._after_generate(path)

    def _open_reports_folder(self) -> None:
        self.pdf_service.refresh_reports_dir()
        os.startfile(self.pdf_service.reports_dir)

    def _select_reports_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения отчётов", str(settings_service.get_reports_dir()))
        if not selected:
            return
        reports_dir = settings_service.set_reports_dir(selected)
        self.pdf_service.refresh_reports_dir()
        self.reports_dir_label.setText(str(reports_dir))
        QMessageBox.information(self, "Папка отчётов", f"Отчёты будут сохраняться в:\n{reports_dir}")

    def _reset_reports_folder(self) -> None:
        reports_dir = settings_service.reset_reports_dir()
        self.pdf_service.refresh_reports_dir()
        self.reports_dir_label.setText(str(reports_dir))
        QMessageBox.information(self, "Папка отчётов", f"Папка отчётов сброшена:\n{reports_dir}")

    def _after_generate(self, path) -> None:
        refill_table(self.reports_table, mock_data.REPORTS)
        QMessageBox.information(self, "PDF", f"PDF сформирован:\n{path}")

    def refresh(self) -> None:
        self.reports_dir_label.setText(str(settings_service.get_reports_dir()))
        refill_table(self.reports_table, mock_data.REPORTS)
