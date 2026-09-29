#!/usr/bin/env python3

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ============================================================
# Configuration
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")

XML_FILE = os.path.join(
    REPORT_DIR,
    "TEST-DemoTestSuite.xml"
)

PDF_FILE = os.path.join(
    REPORT_DIR,
    "ReadyAPI-Test-Report.pdf"
)

PROJECT_NAME = "ReadyAPI-Jenkins-POC"
TEST_SUITE = "DemoTestSuite"


# ============================================================
# Validate XML file
# ============================================================

if not os.path.isfile(XML_FILE):
    print(f"ERROR: JUnit XML file not found:")
    print(XML_FILE)
    sys.exit(1)


# ============================================================
# Read XML
# ============================================================

try:
    root = ET.parse(XML_FILE).getroot()
except Exception as e:
    print(f"ERROR: Unable to read XML report: {e}")
    sys.exit(1)


# ============================================================
# Extract summary
# ============================================================

total_tests = int(root.attrib.get("tests", 0))
failures = int(root.attrib.get("failures", 0))
errors = int(root.attrib.get("errors", 0))
total_time = root.attrib.get("time", "0")

passed_tests = total_tests - failures - errors

overall_status = "PASS"

if failures > 0 or errors > 0:
    overall_status = "FAIL"


# ============================================================
# Extract test cases
# ============================================================

test_cases = []

for testcase in root.findall(".//testcase"):

    test_name = testcase.attrib.get("name", "Unknown")
    classname = testcase.attrib.get("classname", "")
    duration = testcase.attrib.get("time", "0")

    status = "PASS"

    if testcase.find("failure") is not None:
        status = "FAIL"
    elif testcase.find("error") is not None:
        status = "ERROR"
    elif testcase.find("skipped") is not None:
        status = "SKIPPED"

    test_cases.append(
        {
            "name": test_name,
            "classname": classname,
            "duration": duration,
            "status": status,
        }
    )


# ============================================================
# Create PDF
# ============================================================

doc = SimpleDocTemplate(
    PDF_FILE,
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=18 * mm,
)


styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "ReportTitle",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=20,
    spaceAfter=12,
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=13,
    spaceBefore=12,
    spaceAfter=8,
)

normal_style = ParagraphStyle(
    "NormalCustom",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
)

status_style = ParagraphStyle(
    "Status",
    parent=styles["Heading2"],
    alignment=TA_CENTER,
    fontSize=16,
    spaceBefore=10,
    spaceAfter=15,
)


story = []


# ============================================================
# Title
# ============================================================

story.append(
    Paragraph(
        "ReadyAPI Test Execution Report",
        title_style
    )
)

story.append(
    Paragraph(
        f"<b>Overall Result: {overall_status}</b>",
        status_style
    )
)

story.append(Spacer(1, 5))


# ============================================================
# Execution information
# ============================================================

story.append(
    Paragraph(
        "Execution Information",
        heading_style
    )
)

execution_time = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)

execution_data = [
    ["Project", PROJECT_NAME],
    ["Test Suite", TEST_SUITE],
    ["Execution Time", execution_time],
    ["Total Duration", f"{total_time} seconds"],
]


execution_table = Table(
    execution_data,
    colWidths=[55 * mm, 110 * mm],
)

execution_table.setStyle(
    TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]
    )
)

story.append(execution_table)


# ============================================================
# Test Summary
# ============================================================

story.append(
    Paragraph(
        "Test Summary",
        heading_style
    )
)

summary_data = [
    ["Metric", "Count"],
    ["Total Tests", str(total_tests)],
    ["Passed", str(passed_tests)],
    ["Failed", str(failures)],
    ["Errors", str(errors)],
]


summary_table = Table(
    summary_data,
    colWidths=[110 * mm, 55 * mm],
)

summary_table.setStyle(
    TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 1), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]
    )
)

story.append(summary_table)


# ============================================================
# Test Case Details
# ============================================================

story.append(
    Paragraph(
        "Test Case Details",
        heading_style
    )
)

test_data = [
    ["Test Case", "Duration", "Status"]
]

for test in test_cases:

    test_data.append(
        [
            test["name"],
            f'{test["duration"]} sec',
            test["status"],
        ]
    )


test_table = Table(
    test_data,
    colWidths=[90 * mm, 35 * mm, 40 * mm],
)

test_table.setStyle(
    TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]
    )
)

story.append(test_table)


# ============================================================
# Footer
# ============================================================

story.append(Spacer(1, 20))

story.append(
    Paragraph(
        "Generated automatically by Jenkins / ReadyAPI automation.",
        normal_style
    )
)


# ============================================================
# Generate PDF
# ============================================================

try:

    doc.build(story)

except Exception as e:

    print(f"ERROR: Failed to generate PDF: {e}")
    sys.exit(1)


print("")
print("========================================")
print("PDF Report Generated Successfully")
print("========================================")
print(f"PDF: {PDF_FILE}")
print(f"Result: {overall_status}")
print(f"Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failures}")
print(f"Errors: {errors}")
print("========================================")

sys.exit(0)