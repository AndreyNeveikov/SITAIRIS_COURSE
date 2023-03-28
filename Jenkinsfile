pipeline {
    agent {
        docker {
            image 'python:3.10-alpine'
        }
    }
    stages {
        stage('build') {
            steps {
                sh 'python --version'
            }
        }
    }
}