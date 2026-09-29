pipeline {
    agent any

    options {
        timestamps()
    }

    stages {

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

        stage('Wait for ReadyAPI Resource') {
            steps {
                script {
                    echo "Waiting for READYAPI_TESTENGINE resource..."

                    lock(
                        resource: 'READYAPI_TESTENGINE',
                        variable: 'READYAPI_RESOURCE'
                    ) {

                        echo "========================================"
                        echo "READYAPI RESOURCE ACQUIRED"
                        echo "========================================"

                        echo "Resource: ${env.READYAPI_RESOURCE}"

                        stage('Run ReadyAPI Tests') {
                            sh '''
                                echo "========================================"
                                echo "Running ReadyAPI Tests"
                                echo "========================================"

                                chmod +x scripts/run_readyapi.sh

                                ./scripts/run_readyapi.sh
                            '''
                        }

                        stage('Generate PDF Report') {
                            sh '''
                                echo "========================================"
                                echo "Generating PDF Report"
                                echo "========================================"

                                python3 scripts/generate_pdf_report.py
                            '''
                        }

                        echo "========================================"
                        echo "READYAPI RESOURCE WILL BE RELEASED"
                        echo "========================================"
                    }
                }
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