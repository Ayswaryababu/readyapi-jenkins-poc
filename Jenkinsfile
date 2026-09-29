pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify ReadyAPI Project') {
            steps {
                sh '''
                    echo "Workspace:"
                    pwd

                    echo "Files:"
                    find . -maxdepth 3 -type f
                '''
            }
        }

        stage('Run ReadyAPI Tests') {
            steps {
                sh '''
                    /Applications/ReadyAPI-4.2.0.app/Contents/Resources/app/bin/testrunner.sh \
                    -s"DemoTestSuite" \
                    -c"GetUserTest" \
                    -r \
                    "readyapi/ReadyAPI-Jenkins-POC-readyapi-project.xml"
                '''
            }
        }
    }
}