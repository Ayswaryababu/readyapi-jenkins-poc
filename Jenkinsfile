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
    }
}