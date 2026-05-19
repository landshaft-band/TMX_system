from datetime import datetime
from pathlib import Path

from data import mock_data
from services.event_log_service import event_log_service
from services.settings_service import settings_service


class PDFReportService:
    def __init__(self) -> None:
        self.reports_dir = settings_service.get_reports_dir()
        self.reports_dir.mkdir(exist_ok=True)

    def refresh_reports_dir(self) -> Path:
        self.reports_dir = settings_service.get_reports_dir()
        return self.reports_dir

    def generate_shipment_report(self, shipment: dict[str, str]) -> Path:
        rows = mock_data.SHIPMENT_ITEMS.get(shipment["id"], [])
        data = [
            ["ID отгрузки", shipment["id"]],
            ["Статус", shipment["status"]],
            ["Получатель", shipment["recipient"]],
            ["Общий вес", shipment["weight"]],
            ["Количество упаковок", shipment["packages"]],
            ["Статус 1С", shipment["onec_status"]],
        ]
        path = self._build_pdf("Отчёт по отгрузке", f"shipment_{shipment['id']}", data, rows, "Отгрузка сформирована")
        self._register_report("Отчёт по отгрузке", path)
        event_log_service.add_event("PDF_GENERATED", f"Сформирован PDF-отчёт по отгрузке {shipment['id']}", entity_id=shipment["id"])
        return path

    def generate_discrepancy_report(self, discrepancy: list[str]) -> Path:
        data = [
            ["Штрих-код", discrepancy[0]],
            ["Товар", discrepancy[1]],
            ["Плановый вес", discrepancy[2]],
            ["Фактический вес", discrepancy[3]],
            ["Отклонение", discrepancy[4]],
            ["Причина", discrepancy[5]],
            ["Ответственный", mock_data.CURRENT_USER],
        ]
        path = self._build_pdf("Акт расхождения", f"discrepancy_{discrepancy[0]}", data, [], discrepancy[-1])
        self._register_report("Акт расхождения", path)
        event_log_service.add_event("PDF_GENERATED", f"Сформирован PDF-акт расхождения {discrepancy[0]}", entity_id=discrepancy[0])
        return path

    def generate_batch_passport(self, batch: dict[str, str]) -> Path:
        batch_id = batch["id"]
        data = [["Поставка", batch_id], *[[key, value] for key, value in mock_data.BATCH_PASSPORTS[batch_id].items()]]
        path = self._build_pdf("Паспорт партии", f"batch_{batch_id}", data, mock_data.BATCH_ITEMS[batch_id], "Партия готова к контролю")
        self._register_report("Паспорт партии", path)
        event_log_service.add_event("PDF_GENERATED", f"Сформирован PDF-паспорт партии {batch_id}", entity_id=batch_id)
        return path

    def generate_daily_summary_report(self) -> Path:
        data = [
            ["Принято упаковок", str(len(mock_data.ACCEPTED_PACKAGES))],
            ["Проблемных позиций", str(len(mock_data.PROBLEM_POSITIONS))],
            ["Событий в журнале", str(len(mock_data.EVENT_LOG))],
            ["Ошибок синхронизации 1С", str(sum(1 for status in mock_data.ONEC_SYNC_STATUS.values() if status == "Ошибка синхронизации"))],
        ]
        path = self._build_pdf("Суточная сводка", "daily_summary", data, mock_data.EVENT_LOG[:10], "Сводка сформирована")
        self._register_report("Суточная сводка", path)
        event_log_service.add_event("PDF_GENERATED", "Сформирована PDF суточная сводка")
        return path

    def _build_pdf(self, title: str, name: str, data: list[list[str]], table_rows: list[list[str]], status: str) -> Path:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        font_name = "Helvetica"
        font_path = Path("C:/Windows/Fonts/arial.ttf")
        if font_path.exists():
            font_name = "Arial"
            if font_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.refresh_reports_dir()
        path = self.reports_dir / f"{name}_{timestamp}.pdf"
        doc = SimpleDocTemplate(str(path), pagesize=A4)
        styles = getSampleStyleSheet()
        styles["Title"].fontName = font_name
        styles["Normal"].fontName = font_name

        content = [
            Paragraph(title, styles["Title"]),
            Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", styles["Normal"]),
            Paragraph(f"Номер документа: {name.upper()}-{timestamp}", styles["Normal"]),
            Paragraph(f"Пользователь: {mock_data.CURRENT_USER}", styles["Normal"]),
            Spacer(1, 12),
        ]

        content.append(self._table([["Параметр", "Значение"], *data], font_name, colors.lightgrey))
        if table_rows:
            content.append(Spacer(1, 12))
            max_columns = max(len(row) for row in table_rows)
            header = [f"Колонка {index}" for index in range(1, max_columns + 1)]
            content.append(self._table([header, *table_rows], font_name, colors.whitesmoke))
        content.extend([Spacer(1, 12), Paragraph(f"Итоговый статус: {status}", styles["Normal"])])
        doc.build(content)
        return path

    def _table(self, data: list[list[str]], font_name: str, header_color) -> object:
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        data = [[str(cell) for cell in row] for row in data]
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), font_name),
                    ("BACKGROUND", (0, 0), (-1, 0), header_color),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        return table

    def _register_report(self, report_type: str, path: Path) -> None:
        mock_data.REPORTS.insert(
            0,
            [report_type, datetime.now().strftime("%d.%m.%Y %H:%M:%S"), mock_data.CURRENT_USER, str(path)],
        )
