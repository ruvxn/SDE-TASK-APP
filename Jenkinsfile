pipeline {
  agent any
  environment {
    IMAGE = "tasklist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Unit Tests') {
      // Run this stage in a disposable Python container that has pip ready
      agent {
        docker {
          image 'python:3.11-slim'
          args '-u 0'   // runs as root inside the container so pip can install
        }
      }
      steps {
        sh '''
          pip install --no-cache-dir --upgrade pip
          pip install --no-cache-dir -r requirements.txt pytest
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
      // Back on the main Jenkins agent (which has access to the host Docker socket)
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
