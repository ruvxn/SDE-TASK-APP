pipeline {
  agent any
  options { 
    // Prevent the implicit "Declarative: Checkout SCM"
    skipDefaultCheckout(true) 
  }
  environment {
    IMAGE = "tasklist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        // Make sure the workspace is clean before checking out
        deleteDir()
        checkout scm
      }
    }

    stage('Unit Tests') {
      // Run tests inside a Python container (no venv needed)
      agent {
        docker {
          image 'python:3.11-slim'
          args '-u 0'   // run as root inside the container so pip can install
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
