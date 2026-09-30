def sendNotification(String template, String status) {
    def body = readFile("email/${template}")
        .replace('{{PROJECT}}', 'ReadyAPI-Jenkins-POC')
        .replace('{{TEST_SUITE}}', env.READYAPI_SUITE)
        .replace('{{TEST_CASE}}', env.READYAPI_CASE)
        .replace('{{BUILD_NUMBER}}', env.BUILD_NUMBER)
        .replace('{{BUILD_URL}}', env.BUILD_URL)

    emailext(
        to: params.REQUESTER_EMAIL,
        subject: "ReadyAPI Test Result - ${env.JOB_NAME} #${env.BUILD_NUMBER} - ${status}",
        body: body,
        mimeType: 'text/html',
        attachmentsPattern: 'reports/ReadyAPI-Test-Report.pdf'
    )
}

pipeline {
    agent any

    parameters {
        string(
            name: 'REQUESTER_EMAIL',
            defaultValue: '',
            description: 'Email address to receive the test report'
        )

        booleanParam(
            name: 'ENABLE_TEST_HOLD',
            defaultValue: true,
            description: 'Hold the shared resource for 2 minutes for queue testing'
        )
    }

    // Pipeline configuration
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    // ReadyAPI configuration
    environment {
        READYAPI_RESOURCE = 'READYAPI_TESTENGINE'
        READYAPI_SUITE = 'DemoTestSuite'
        READYAPI_CASE = 'GetUserTest'

        READYAPI_RUNNER =
            '/Applications/ReadyAPI-4.2.0.app/Contents/Resources/app/bin/testrunner.sh'

        READYAPI_PROJECT =
            'readyapi/ReadyAPI-Jenkins-POC-readyapi-project.xml'
    }

    stages {

        // ============================================================
        // Checkout source code
        // ============================================================
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ============================================================
        // Validate required configuration and dependencies
        // ============================================================
        stage('Validate') {
            steps {
                script {
                    if (!params.REQUESTER_EMAIL?.trim()) {
                        error('REQUESTER_EMAIL is required.')
                    }
                }

                sh '''
                    echo "Validating ReadyAPI environment..."

                    test -x "$READYAPI_RUNNER" || {
                        echo "ERROR: ReadyAPI runner not found:"
                        echo "$READYAPI_RUNNER"
                        exit 1
                    }

                    test -f "$READYAPI_PROJECT" || {
                        echo "ERROR: ReadyAPI project not found:"
                        echo "$READYAPI_PROJECT"
                        exit 1
                    }

                    python3 --version

                    echo "Validation completed successfully."
                '''
            }
        }

        // ============================================================
        // Execute ReadyAPI using shared lock
        // ============================================================
        stage('Execute ReadyAPI') {
            steps {
                script {

                    lock(
                        resource: env.READYAPI_RESOURCE,
                        variable: 'LOCKED_RESOURCE'
                    ) {

                        echo "========================================"
                        echo "Shared ReadyAPI resource acquired"
                        echo "Resource: ${env.LOCKED_RESOURCE}"
                        echo "========================================"

                        timeout(time: 20, unit: 'MINUTES') {

                            /*
                             * Important:
                             *
                             * ReadyAPI returns a non-zero exit code when
                             * the test case fails.
                             *
                             * catchError allows the pipeline to continue
                             * to Generate Report and Archive Results.
                             *
                             * The Jenkins build is still marked FAILURE.
                             */
                            catchError(
                                buildResult: 'FAILURE',
                                stageResult: 'FAILURE'
                            ) {
                                sh '''
                                    chmod +x scripts/run_readyapi.sh

                                    ./scripts/run_readyapi.sh
                                '''
                            }
                        }

                        echo "ReadyAPI execution completed."

                        // ------------------------------------------------
                        // Temporary 2-minute hold for queue testing
                        // ------------------------------------------------
                        if (params.ENABLE_TEST_HOLD) {

                            echo "========================================"
                            echo "Holding shared resource for 2 minutes"
                            echo "This is enabled for queue testing."
                            echo "========================================"

                            sleep(
                                time: 2,
                                unit: 'MINUTES'
                            )

                            echo "2-minute resource hold completed."
                        }

                        echo "Shared ReadyAPI resource will now be released."
                    }
                }
            }
        }

        // ============================================================
        // Generate readable PDF report
        // ============================================================
        stage('Generate Report') {
            steps {
                echo "Generating PDF test report..."

                sh '''
                    python3 scripts/generate_pdf_report.py
                '''
            }
        }

        // ============================================================
        // Archive test results
        // ============================================================
        stage('Archive Results') {
            steps {
                echo "Archiving ReadyAPI test results..."

                archiveArtifacts(
                    artifacts:
                        'reports/ReadyAPI-Test-Report.pdf,' +
                        'reports/TEST-DemoTestSuite.xml,' +
                        'reports/readyapi-console.log',
                    fingerprint: true,
                    allowEmptyArchive: false
                )
            }
        }
    }

    // ================================================================
    // Notifications
    // ================================================================
    post {

        always {
            echo "========================================"
            echo "Build #${env.BUILD_NUMBER}"
            echo "Final Result: ${currentBuild.currentResult}"
            echo "========================================"
        }

        success {
            script {
                sendNotification(
                    'success.html',
                    'PASSED'
                )
            }
        }

        failure {
            script {
                sendNotification(
                    'failure.html',
                    'FAILED'
                )
            }
        }

        aborted {
            script {
                sendNotification(
                    'aborted.html',
                    'ABORTED/TIMEOUT'
                )
            }
        }

        // ============================================================
        // Clean workspace after artifacts/email are completed
        // ============================================================
        cleanup {
            echo "Cleaning Jenkins workspace..."

            deleteDir()
        }
    }
}