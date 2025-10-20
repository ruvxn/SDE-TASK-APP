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
  agent {
    docker {
      image 'python:3.11-slim'
      args '-u 0'   // root in the container so pip can install
    }
  }
  steps {
    sh '''
      set -euxo pipefail
      echo ">>> Working dir:"; pwd
      echo ">>> Python:"; python -V
      echo ">>> Repo contents (top-level):"
      ls -la
      echo ">>> Tests directory (if present):"
      [ -d tests ] && ls -la tests || true

      # Install deps
      pip install --no-cache-dir --upgrade pip
      pip install --no-cache-dir -r requirements.txt pytest

      # If pytest.ini / pyproject.toml misconfigures testpaths,
      # ignore repo config (-c /dev/null) and explicitly point to tests/.
      # Fall back to running from repo root if there is no tests/ dir.
      if [ -d tests ]; then
        pytest -q -c /dev/null tests --junitxml=pytest-results.xml
      else
        pytest -q -c /dev/null --junitxml=pytest-results.xml
      fi
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
