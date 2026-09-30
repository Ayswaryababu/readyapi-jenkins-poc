# ReadyAPI Jenkins Automation POC

Enterprise-style CI/CD automation framework for executing **ReadyAPI functional tests through Jenkins**, managing concurrent test requests with a shared execution lock, generating readable PDF reports, archiving test evidence, and notifying requesters through email.

---

## Overview

This project demonstrates a Jenkins-based automation framework for centralized ReadyAPI test execution.

The solution is designed around a shared ReadyAPI execution resource where multiple users or teams can submit test requests without directly consuming a ReadyAPI GUI session.

Jenkins manages the execution workflow, while **Lockable Resources** controls access to the shared ReadyAPI execution slot.

### Key capabilities

* ReadyAPI CLI-based automated test execution
* Jenkins declarative pipeline
* Multiple concurrent build requests
* Shared-resource queue management
* Lock-based ReadyAPI execution control
* Automated JUnit XML result generation
* Human-readable PDF report generation
* Email notification with PDF attachment
* Jenkins artifact archival
* Automated workspace cleanup
* Configurable requester email
* Build timeout and failure handling
* Git-based source control
* Separation of scripts, test assets, reporting, and notifications

---

## Architecture

```text
                    ┌──────────────────────┐
                    │      Developer /     │
                    │      Test Team       │
                    └──────────┬───────────┘
                               │
                               │ Trigger Jenkins
                               ▼
                    ┌──────────────────────┐
                    │       Jenkins        │
                    │ Declarative Pipeline │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌──────────────────┐
       │ Checkout /      │          │ Multiple Build   │
       │ Validation      │          │ Requests         │
       └────────┬────────┘          └────────┬─────────┘
                │                            │
                └──────────────┬─────────────┘
                               ▼
                    ┌──────────────────────┐
                    │  Lockable Resource   │
                    │ READYAPI_TESTENGINE   │
                    └──────────┬───────────┘
                               │
                     One execution at a time
                               │
                               ▼
                    ┌──────────────────────┐
                    │     ReadyAPI CLI     │
                    │     Test Runner      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ JUnit XML + Console  │
                    │       Results        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ PDF Report Generator │
                    │      ReportLab       │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌─────────────────┐          ┌──────────────────┐
       │ Jenkins         │          │ Email Extension  │
       │ Artifacts       │          │ PDF Notification │
       └─────────────────┘          └──────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Workspace Cleanup    │
                    └──────────────────────┘
```

---

## Execution Model

Multiple users can trigger the Jenkins job simultaneously.

The Jenkins job itself is allowed to create concurrent builds. The shared ReadyAPI execution resource is controlled independently using the **Lockable Resources** plugin.

Example:

```text
Build #101 → Running ReadyAPI
Build #102 → Waiting for READYAPI_TESTENGINE
Build #103 → Waiting for READYAPI_TESTENGINE
Build #104 → Waiting for READYAPI_TESTENGINE
```

After Build #101 releases the resource:

```text
Build #102 → Running ReadyAPI
Build #103 → Waiting
Build #104 → Waiting
```

This separates:

* **Build concurrency**
* **ReadyAPI execution concurrency**

Only the ReadyAPI execution section is serialized.

---

## Technology Stack

| Component                    | Purpose                              |
| ---------------------------- | ------------------------------------ |
| Jenkins                      | CI/CD orchestration                  |
| Jenkins Declarative Pipeline | Pipeline implementation              |
| ReadyAPI                     | Functional/API test execution        |
| ReadyAPI CLI                 | Headless test execution              |
| Lockable Resources           | Shared execution resource management |
| Python                       | PDF report generation                |
| ReportLab                    | PDF generation                       |
| Email Extension Plugin       | Email notifications                  |
| GitHub                       | Source control                       |
| macOS                        | Current POC execution environment    |

---

## Project Structure

```text
ReadyAPI-Jenkins-POC/
│
├── Jenkinsfile
│
├── readyapi/
│   └── ReadyAPI-Jenkins-POC-readyapi-project.xml
│
├── scripts/
│   ├── run_readyapi.sh
│   └── generate_pdf_report.py
│
├── email/
│   ├── success.html
│   ├── failure.html
│   └── aborted.html
│
└── README.md
```

### Directory Responsibilities

#### `Jenkinsfile`

Defines the complete CI/CD workflow:

* Source checkout
* Dependency validation
* Shared-resource locking
* ReadyAPI execution
* Report generation
* Artifact archival
* Email notification
* Workspace cleanup

#### `readyapi/`

Contains the ReadyAPI project definition used by the automation pipeline.

#### `scripts/`

Contains reusable automation scripts.

`run_readyapi.sh`

* Validates the ReadyAPI environment
* Executes ReadyAPI CLI
* Generates JUnit-compatible results
* Captures console output
* Returns the ReadyAPI exit code

`generate_pdf_report.py`

* Reads the ReadyAPI JUnit XML result
* Extracts test execution information
* Generates a human-readable PDF report
* Reports PASS/FAIL status

#### `email/`

Contains external HTML email templates.

This keeps notification content separate from pipeline logic.

---

# Pipeline Workflow

## 1. Checkout

Jenkins retrieves the latest source code from GitHub.

```text
GitHub
   ↓
Jenkins Workspace
```

---

## 2. Validation

The pipeline validates required dependencies before starting the test.

Examples:

```text
ReadyAPI Test Runner
ReadyAPI Project XML
Python
```

If a required dependency is missing, the pipeline stops before test execution.

---

## 3. Acquire Shared Resource

The pipeline requests:

```text
READYAPI_TESTENGINE
```

This is currently used as a **logical shared execution resource** for the POC.

The resource represents the single ReadyAPI execution slot.

> Note: The current POC does not integrate with the ReadyAPI TestEngine server. The resource name is retained to model the enterprise shared-license/execution-slot architecture.

---

## 4. Execute ReadyAPI

The pipeline executes the ReadyAPI project using the CLI runner.

Example:

```bash
testrunner.sh \
  -s"DemoTestSuite" \
  -c"GetUserTest" \
  -r \
  -j \
  -f"reports" \
  "readyapi/ReadyAPI-Jenkins-POC-readyapi-project.xml"
```

The test execution generates:

* JUnit XML
* Console log
* ReadyAPI report data

---

## 5. Release Shared Resource

Once ReadyAPI execution completes, the shared resource is released.

Other queued Jenkins builds can then acquire the resource.

---

## 6. Generate PDF Report

The pipeline executes:

```bash
python3 scripts/generate_pdf_report.py
```

The script converts the ReadyAPI JUnit result into:

```text
ReadyAPI-Test-Report.pdf
```

The report contains execution information such as:

* Test result
* Total tests
* Passed tests
* Failed tests
* Errors
* Execution duration
* Test case details

---

## 7. Archive Test Evidence

Only the required artifacts are retained by Jenkins:

```text
reports/ReadyAPI-Test-Report.pdf
reports/TEST-DemoTestSuite.xml
reports/readyapi-console.log
```

This avoids unnecessarily archiving the complete ReadyAPI-generated HTML report directory.

---

## 8. Email Notification

The Email Extension plugin sends a notification to the requester.

The requester is supplied through the Jenkins parameter:

```text
REQUESTER_EMAIL
```

Example:

```text
REQUESTER_EMAIL = user@example.com
```

The email includes:

* Project name
* Test suite
* Test case
* Build number
* Build URL
* Execution status
* PDF report attachment

Email templates are maintained separately under:

```text
email/
```

---

## 9. Workspace Cleanup

After the pipeline has completed its notification and archival activities, Jenkins removes the workspace.

The pipeline uses:

```groovy
post {
    cleanup {
        deleteDir()
    }
}
```

This prevents generated files from accumulating between builds.

Archived Jenkins artifacts remain available even after the workspace is deleted.

---

# Jenkins Configuration

## Required Plugins

The POC uses the following Jenkins plugins:

### Lockable Resources

Used to control access to the shared ReadyAPI execution resource.

Resource:

```text
READYAPI_TESTENGINE
```

### Email Extension

Used for HTML email notifications and PDF attachments.

### Git

Used for source-code checkout.

---

# Jenkins Parameters

The pipeline supports configurable execution parameters.

## `REQUESTER_EMAIL`

Email address receiving the test result.

Example:

```text
user@example.com
```

The email address is supplied at runtime and is not stored in GitHub.

## `ENABLE_TEST_HOLD`

Used for queue/concurrency testing.

```text
true
```

When enabled, the pipeline holds the shared resource for two minutes after ReadyAPI execution.

This makes it easier to demonstrate queued builds.

For normal execution:

```text
false
```

---

# Security

No credentials are stored in the GitHub repository.

The following information must remain inside Jenkins:

* SMTP credentials
* Gmail App Password
* API credentials
* Tokens
* Other secrets

The repository contains only pipeline logic and test automation assets.

### Recommended practices

* Store credentials using Jenkins Credentials Manager.
* Never hard-code passwords or tokens.
* Avoid committing production secrets.
* Avoid committing sensitive test data.
* Use Jenkins parameters for runtime requester information.
* Use environment variables or Jenkins credentials for sensitive configuration.

---

# Email Configuration

For the current POC, Jenkins is configured to use Gmail SMTP.

Typical configuration:

```text
SMTP Server : smtp.gmail.com
Port        : 587
TLS         : Enabled
Credentials : Jenkins-managed Gmail credential
```

The Gmail App Password is stored securely in Jenkins and is **not committed to GitHub**.

---

# ReadyAPI Test Project

Current test structure:

```text
ReadyAPI-Jenkins-POC
└── DemoTestSuite
    └── GetUserTest
        └── GetUser
```

Test endpoint:

```text
https://jsonplaceholder.typicode.com/users/1
```

Current assertions include:

```text
Valid HTTP Status Codes
Response SLA
```

The project is intentionally lightweight and is used to validate the Jenkins automation framework.

---

# Current Execution Flow

```text
Developer/Test Team
        │
        ▼
Trigger Jenkins
        │
        ▼
Checkout Repository
        │
        ▼
Validate Environment
        │
        ▼
Wait for Shared Resource
        │
        ▼
Acquire READYAPI_TESTENGINE
        │
        ▼
Execute ReadyAPI CLI
        │
        ▼
Generate JUnit XML
        │
        ▼
Release Shared Resource
        │
        ▼
Generate PDF
        │
        ▼
Archive Results
        │
        ▼
Send Email
        │
        ▼
Clean Workspace
```

---

# Failure Handling

The pipeline is designed to fail fast when required dependencies are unavailable.

Examples:

### ReadyAPI runner unavailable

```text
ERROR: ReadyAPI runner not found.
```

Pipeline status:

```text
FAILED
```

### ReadyAPI project unavailable

```text
ERROR: ReadyAPI project not found.
```

Pipeline status:

```text
FAILED
```

### ReadyAPI test failure

The ReadyAPI exit code is returned to Jenkins.

The pipeline is marked:

```text
FAILED
```

The failure notification is sent using:

```text
email/failure.html
```

### Pipeline timeout

The pipeline has an overall timeout to prevent indefinitely running jobs.

The aborted notification uses:

```text
email/aborted.html
```

---

# Timeout Strategy

The pipeline uses layered timeout protection.

Example:

```text
Overall Pipeline
       │
       └── 30 minutes maximum
                │
                └── ReadyAPI execution
                         │
                         └── 20 minutes maximum
```

This protects the shared execution resource from an indefinitely running test.

---

# Artifact Strategy

The pipeline intentionally separates **workspace files** from **Jenkins artifacts**.

### Workspace

Temporary:

```text
reports/
scripts/
readyapi/
```

The workspace is deleted after pipeline completion.

### Jenkins Artifacts

Persistent build evidence:

```text
ReadyAPI-Test-Report.pdf
TEST-DemoTestSuite.xml
readyapi-console.log
```

This allows previous builds to retain their test evidence without retaining the complete workspace.

---

# Local Development

## Prerequisites

Install/configure:

* Git
* Jenkins
* ReadyAPI
* Python 3
* ReportLab
* Jenkins Lockable Resources plugin
* Jenkins Email Extension plugin

Verify ReadyAPI:

```bash
ls -l /Applications/ReadyAPI-4.2.0.app/Contents/Resources/app/bin/testrunner.sh
```

Verify Python:

```bash
python3 --version
```

---

# Run ReadyAPI Locally

From the repository root:

```bash
chmod +x scripts/run_readyapi.sh
./scripts/run_readyapi.sh
```

Expected result:

```text
RESULT: PASS
```

---

# Generate PDF Locally

After a successful ReadyAPI execution:

```bash
python3 scripts/generate_pdf_report.py
```

Expected output:

```text
PDF Report Generated Successfully
Result: PASS
Tests: 1
Passed: 1
Failed: 0
Errors: 0
```

Generated report:

```text
reports/ReadyAPI-Test-Report.pdf
```

---

# Jenkins Pipeline Setup

Create a Jenkins Pipeline job and configure it to use the GitHub repository.

Recommended configuration:

```text
Pipeline Definition:
Pipeline script from SCM

SCM:
Git

Repository:
ReadyAPI-Jenkins-POC

Script Path:
Jenkinsfile
```

Because the repository is public, no GitHub credentials are required for this POC repository.

---

# Queue Validation

To validate shared-resource behavior:

1. Trigger Build #1.
2. Keep `ENABLE_TEST_HOLD=true`.
3. Trigger Build #2 immediately.
4. Trigger Build #3 immediately.
5. Observe Jenkins queue.

Expected:

```text
Build #1 → Running
Build #2 → Waiting for READYAPI_TESTENGINE
Build #3 → Waiting for READYAPI_TESTENGINE
```

After Build #1 releases the resource:

```text
Build #2 → Running
Build #3 → Waiting
```

This validates that Jenkins can accept multiple requests while the shared ReadyAPI execution resource remains serialized.

---

# Repository Branching

Recommended Git workflow:

```text
main
 │
 ├── feature/<name>
 ├── bugfix/<name>
 └── enhancement/<name>
```

Example:

```bash
git checkout -b feature/improve-readyapi-report
```

Commit changes:

```bash
git add .
git commit -m "Improve ReadyAPI execution reporting"
```

Push:

```bash
git push origin feature/improve-readyapi-report
```

---

# Design Principles

This POC follows several enterprise automation principles:

### Separation of concerns

Pipeline orchestration, test execution, reporting, and notifications are maintained separately.

### Reusability

Shell and Python scripts can be reused outside Jenkins.

### Configuration over hard-coding

Runtime values such as requester email are provided through Jenkins parameters.

### Secure credential management

Credentials remain in Jenkins instead of source control.

### Controlled concurrency

Shared execution resources are protected using Lockable Resources.

### Traceability

Each Jenkins build retains test evidence through archived artifacts.

### Automated cleanup

Temporary workspace data is removed after execution.

---

# Current Scope

The current POC demonstrates:

* Jenkins orchestration
* ReadyAPI CLI execution
* Shared-resource queueing
* Automated reporting
* PDF generation
* Email notification
* Artifact archival
* Workspace cleanup

The POC intentionally uses **local ReadyAPI CLI execution**.

ReadyAPI TestEngine server integration is outside the current scope.

---

# Future Enhancements

Potential enterprise extensions include:

* ReadyAPI TestEngine integration
* Dedicated Jenkins agents
* Docker-based execution environment
* Parameterized ReadyAPI environments
* Multiple ReadyAPI projects
* Dynamic test suite/test case selection
* Environment selection such as DEV/SI/PROD
* Parallel execution for independent test groups
* Centralized test reporting
* Allure/HTML reporting integration
* Slack or Microsoft Teams notifications
* Test result dashboards
* Role-based Jenkins access
* Credential rotation
* SonarQube/security scanning
* CI quality gates
* Automated GitHub pull-request validation
* Infrastructure-as-Code deployment
* Cloud-hosted execution workers

---

# Project Outcome

This POC demonstrates how a centralized Jenkins automation framework can provide:

```text
Self-Service Test Execution
          +
Shared Resource Management
          +
Automated Test Reporting
          +
Email Notification
          +
Build Traceability
          +
Workspace Lifecycle Management
```

The architecture can subsequently be extended from a local POC into a centralized enterprise ReadyAPI automation platform.
