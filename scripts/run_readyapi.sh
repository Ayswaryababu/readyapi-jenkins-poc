#!/bin/bash

set -u

# ============================================================
# ReadyAPI Jenkins Automation Runner
# ============================================================

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Project root = one level above scripts/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ReadyAPI installation
READYAPI_HOME="/Applications/ReadyAPI-4.2.0.app/Contents/Resources/app"
TEST_RUNNER="$READYAPI_HOME/bin/testrunner.sh"

# ReadyAPI project
PROJECT_FILE="$PROJECT_ROOT/readyapi/ReadyAPI-Jenkins-POC-readyapi-project.xml"

# Test details
TEST_SUITE="DemoTestSuite"
TEST_CASE="GetUserTest"

# Report directory
REPORT_DIR="$PROJECT_ROOT/reports"

# Console log
LOG_FILE="$REPORT_DIR/readyapi-console.log"

# ============================================================
# Create report directory
# ============================================================

mkdir -p "$REPORT_DIR"

# ============================================================
# Validation
# ============================================================

echo "========================================"
echo "ReadyAPI Automation Execution"
echo "========================================"

echo "Project Root : $PROJECT_ROOT"
echo "ReadyAPI     : $READYAPI_HOME"
echo "Test Runner  : $TEST_RUNNER"
echo "Project File : $PROJECT_FILE"
echo "Test Suite   : $TEST_SUITE"
echo "Test Case    : $TEST_CASE"
echo "Report Dir   : $REPORT_DIR"
echo "========================================"

if [ ! -f "$TEST_RUNNER" ]; then
    echo "ERROR: ReadyAPI test runner not found:"
    echo "$TEST_RUNNER"
    exit 1
fi

if [ ! -f "$PROJECT_FILE" ]; then
    echo "ERROR: ReadyAPI project file not found:"
    echo "$PROJECT_FILE"
    exit 1
fi

# ============================================================
# Clean previous generated reports
# ============================================================

echo ""
echo "Preparing report directory..."

mkdir -p "$REPORT_DIR"

# ============================================================
# Run ReadyAPI
# ============================================================

echo ""
echo "Starting ReadyAPI test..."
echo ""

"$TEST_RUNNER" \
    -s"$TEST_SUITE" \
    -c"$TEST_CASE" \
    -r \
    -j \
    -f"$REPORT_DIR" \
    "$PROJECT_FILE" \
    2>&1 | tee "$LOG_FILE"

# ============================================================
# Capture ReadyAPI exit code
# ============================================================

READYAPI_EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "========================================"
echo "ReadyAPI Execution Completed"
echo "========================================"

echo "ReadyAPI exit code: $READYAPI_EXIT_CODE"

# ============================================================
# Display generated reports
# ============================================================

echo ""
echo "Generated files:"
find "$REPORT_DIR" -maxdepth 3 -type f -print

echo ""
echo "========================================"

# ============================================================
# Return ReadyAPI result to Jenkins
# ============================================================

if [ "$READYAPI_EXIT_CODE" -eq 0 ]; then
    echo "RESULT: PASS"
    echo "========================================"
    exit 0
else
    echo "RESULT: FAIL"
    echo "========================================"
    exit "$READYAPI_EXIT_CODE"
fi