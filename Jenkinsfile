pipeline{
    agent any
    stages{
        stage('Build Docker Image'){
            steps{
                bat 'docker build -t 0d_calculation_aws_img_jenk .' 
            }
        }
        stage('List Docker Images'){
            steps{
                bat 'docker images'
            }
        }
        stage('create Docker Container'){
            steps{
                bat 'docker run --rm -p 9000:5000 --name=0d_calculation_aws_cont_jenk 0d_calculation_aws_img_jenk'
            }
        }
    }
    
}