pipeline {
    agent any
    stages {
        stage('Build and test the project') {
            steps {
                sh 'docker-compose down'
            }
        }
        stage('Run tests') {
            steps {
                sh 'docker-compose run web pytest src/tests'
            }
        }
        stage('Down') {
            steps {
                sh 'docker-compose down'
            }
        }
    }
}
