pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t 0d_calculation_aws_img_jenk .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh '''
                docker stop 0d_calculation_aws_cont_jenk || true
                docker rm 0d_calculation_aws_cont_jenk || true
                '''
            }
        }

        stage('List Docker Images') {
            steps {
                sh 'docker images'
            }
        }

        stage('Create Docker Container') {
            steps {
                sh 'docker run -d --rm -p 80:5000 --name=0d_calculation_aws_cont_jenk 0d_calculation_aws_img_jenk'
            }
        }
    }
}
