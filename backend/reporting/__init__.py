"""
Reporting Module
================

Contains presentation-layer report formatters.
These modules format existing data - they do NOT calculate or modify data.
"""

from .yoyo_report_v2 import (
    YoYoReportV2Formatter,
    format_yoyo_report_v2,
    validate_report_structure,
    SECTION_TITLES
)

__all__ = [
    'YoYoReportV2Formatter',
    'format_yoyo_report_v2',
    'validate_report_structure',
    'SECTION_TITLES'
]
