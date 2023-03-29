pipeline {
    agent any
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'python:3.10'
                    args "--user root --privileged"
                }
            }
            stages {
                stage('Install dependencies') {
                    steps {
                        sh 'pip install --upgrade pip'
                        sh 'pip install poetry'
                        sh 'poetry config virtualenvs.create false'
                        sh 'poetry install --no-interaction'
                    }
                }
                stage('Autoformat') {
                    steps {
                        sh 'isort .'
                        sh 'black .'

                    }
                }
                stage('Lint') {
                    steps {
                        sh 'flake8'
                    }
                }
            }
        }
        stage('Testing') {
            steps {
                sh 'docker-compose run web pytest src/tests/'
            }
        }
    }
}