pipeline{
    agent any
    stages{
        stage('Build Docker Image'){
            step{
                bat 'docker build -t 0d_calculation_aws_img_jenk .' 
            }
        }
        state('List Docker Images'){
            step{
                bat 'docker images'
            }
        }
        stage('create Docker Container'){
            step{
                bat 'docker run --rm -p 9000:5000 --name=0d_calculation_aws_cont_jenk 0d_calculation_aws_img_jenk'
            }
        }
    }
    
}