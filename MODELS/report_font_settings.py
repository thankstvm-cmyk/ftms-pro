from dataclasses import dataclass
@dataclass
class ReportFontSettings:
    company_name_font: str = "Arial Bold"
    report_title_font: str = "Arial Bold"
    heading_font: str = "Calibri Bold"
    body_font: str = "Arial"
    footer_font: str = "Calibri"