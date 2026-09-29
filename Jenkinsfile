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
        disableConcurrentBuilds(abortPrevious: false)
        timeout(time: 30, unit: 'MINUTES')
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    // ReadyAPI configuration
    environment {
        READYAPI_RESOURCE = 'READYAPI_TESTENGINE'
        READYAPI_SUITE = 'DemoTestSuite'
        READYAPI_CASE = 'GetUserTest'
        READYAPI_RUNNER = '/Applications/ReadyAPI-4.2.0.app/Contents/Resources/app/bin/testrunner.sh'
        READYAPI_PROJECT = 'readyapi/ReadyAPI-Jenkins-POC-readyapi-project.xml'
    }

    stages {

        // Checkout source
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // Validate required dependencies
        stage('Validate') {
            steps {
                script {
                    if (!params.REQUESTER_EMAIL?.trim()) {
                        error('REQUESTER_EMAIL is required.')
                    }
                }

                sh '''
                    test -x "$READYAPI_RUNNER" || {
                        echo "ERROR: ReadyAPI runner not found."
                        exit 1
                    }

                    test -f "$READYAPI_PROJECT" || {
                        echo "ERROR: ReadyAPI project not found."
                        exit 1
                    }

                    python3 --version
                '''
            }
        }

        // Acquire shared resource and execute ReadyAPI
        stage('Execute ReadyAPI') {
            steps {
                script {
                    lock(
                        resource: env.READYAPI_RESOURCE,
                        variable: 'LOCKED_RESOURCE'
                    ) {
                        echo "Acquired: ${env.LOCKED_RESOURCE}"

                        timeout(time: 20, unit: 'MINUTES') {
                            sh '''
                                chmod +x scripts/run_readyapi.sh
                                ./scripts/run_readyapi.sh
                            '''
                        }

                        echo 'ReadyAPI execution completed.'

                        // Temporary hold for queue testing
                        if (params.ENABLE_TEST_HOLD) {
                            echo 'Holding shared resource for 2 minutes...'
                            sleep(time: 2, unit: 'MINUTES')
                        }
                    }
                }
            }
        }

        // Generate readable PDF report
        stage('Generate Report') {
            steps {
                sh 'python3 scripts/generate_pdf_report.py'
            }
        }

        // Store reports in Jenkins
        stage('Archive Results') {
            steps {
                archiveArtifacts(
                    artifacts: 'reports/ReadyAPI-Test-Report.pdf,reports/TEST-DemoTestSuite.xml,reports/readyapi-console.log',
                    fingerprint: true,
                    allowEmptyArchive: false
                )
            }
        }
    }

    // Send result notification
    post {
        always {
            echo "Build #${env.BUILD_NUMBER}: ${currentBuild.currentResult}"
        }

        success {
            script {
                sendNotification('success.html', 'PASSED')
            }
        }

        failure {
            script {
                sendNotification('failure.html', 'FAILED')
            }
        }

        aborted {
            script {
                sendNotification('aborted.html', 'ABORTED/TIMEOUT')
            }
        }
        cleanup {
            deleteDir()
        }
    }
}