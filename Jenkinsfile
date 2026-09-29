pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify ReadyAPI Project') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Workspace"
                    echo "========================================"

                    pwd

                    echo ""
                    echo "Repository files:"
                    find . -maxdepth 3 -type f -print
                '''
            }
        }

        stage('Run ReadyAPI Tests') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Running ReadyAPI Tests"
                    echo "========================================"

                    chmod +x scripts/run_readyapi.sh

                    ./scripts/run_readyapi.sh
                '''
            }
        }

        stage('Generate PDF Report') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Generating PDF Report"
                    echo "========================================"

                    python3 scripts/generate_pdf_report.py
                '''
            }
        }

        stage('Archive Reports') {
            steps {
                archiveArtifacts(
                    artifacts: 'reports/**/*',
                    fingerprint: true,
                    allowEmptyArchive: false
                )
            }
        }
    }

    post {
        always {
            echo "ReadyAPI automation completed."
        }

        success {
            echo "ReadyAPI automation PASSED."
        }

        failure {
            echo "ReadyAPI automation FAILED."
        }
    }
}