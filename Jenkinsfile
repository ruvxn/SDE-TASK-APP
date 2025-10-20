pipeline {
  agent any
  environment {
    IMAGE = "your-dockerhub-username/tasklist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
    SSH_HOST = "ec2-user@YOUR_EC2_PUBLIC_IP"
  }
  options { timestamps() }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Unit Tests') {
      steps {
        sh '''
          python3 -m venv venv
          . venv/bin/activate
          pip install -r requirements.txt pytest
          pytest -q
        '''
      }
      post {
        always { junit testResults: '**/pytest*.xml', allowEmptyResults: true }
      }
    }
    stage('Build Image') {
      steps {
        sh 'docker build -t $IMAGE .'
      }
    }
    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DU', passwordVariable: 'DP')]) {
          sh '''
            echo "$DP" | docker login -u "$DU" --password-stdin
            docker push $IMAGE
          '''
        }
      }
    }
    stage('Deploy to EC2') {
      steps {
        sshagent (credentials: ['ec2-ssh']) {
          sh '''
            ssh -o StrictHostKeyChecking=no $SSH_HOST "export APP_IMAGE=$IMAGE && \
              mkdir -p ~/app && \
              cd ~/app && \
              echo \\"APP_IMAGE=$IMAGE\\" > .env && \
              docker compose -f docker-compose.prod.yml pull && \
              docker compose -f docker-compose.prod.yml up -d --remove-orphans"
          '''
        }
      }
    }
  }
  post {
    success { echo 'Deploy complete.' }
    failure { echo 'Build failed.' }
  }
}
