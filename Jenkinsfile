pipeline {
  agent any
  environment {
    IMAGE = "tasklist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Set up Python & Install Deps') {
      steps {
        sh '''
          python3 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt pytest
        '''
      }
    }
    stage('Run Tests') {
      steps {
        sh '''
          . venv/bin/activate
          pytest -q --junitxml=pytest-results.xml
        '''
      }
      post {
        always {
          junit testResults: 'pytest-results.xml', allowEmptyResults: true
        }
      }
    }
    stage('Build Docker Image') {
      steps {
        sh 'docker build -t $IMAGE .'
      }
    }
  }
  post {
    success { echo "Level 1 CI pipeline finished successfully." }
    failure { echo "Level 1 CI pipeline failed." }
  }
}
