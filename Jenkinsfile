pipeline {
    agent any

    parameters {
        string(
            name: 'REQUESTER_EMAIL',
            defaultValue: '',
            description: 'Email address to receive the ReadyAPI test report'
        )
    }

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

                    if (!params.REQUESTER_EMAIL?.trim()) {
                        error("REQUESTER_EMAIL parameter is required.")
                    }

                    echo "========================================"
                    echo "Waiting for READYAPI_TESTENGINE resource"
                    echo "========================================"

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
            echo "========================================"
            echo "ReadyAPI automation completed."
            echo "Requester: ${params.REQUESTER_EMAIL}"
            echo "========================================"
        }

        success {
            echo "ReadyAPI automation PASSED."

            emailext(
                subject: "ReadyAPI Test Result - ${env.JOB_NAME} #${env.BUILD_NUMBER} - PASSED",

                body: """
Hello,

The ReadyAPI automation execution has completed successfully.

Project     : ReadyAPI-Jenkins-POC
Test Suite  : DemoTestSuite
Test Case   : GetUserTest
Build       : #${env.BUILD_NUMBER}
Result      : PASSED

The ReadyAPI PDF test report is attached to this email.

Jenkins Build:
${env.BUILD_URL}

Regards,
Jenkins
""",

                attachmentsPattern: 'reports/ReadyAPI-Test-Report.pdf',

                to: "${params.REQUESTER_EMAIL}"
            )
        }

        failure {
            echo "ReadyAPI automation FAILED."

            emailext(
                subject: "ReadyAPI Test Result - ${env.JOB_NAME} #${env.BUILD_NUMBER} - FAILED",

                body: """
Hello,

The ReadyAPI automation execution has failed.

Project     : ReadyAPI-Jenkins-POC
Test Suite  : DemoTestSuite
Test Case   : GetUserTest
Build       : #${env.BUILD_NUMBER}
Result      : FAILED

Please check the Jenkins console output and archived reports.

Jenkins Build:
${env.BUILD_URL}

Regards,
Jenkins
""",

                attachmentsPattern: 'reports/ReadyAPI-Test-Report.pdf',

                to: "${params.REQUESTER_EMAIL}"
            )
        }
    }
}