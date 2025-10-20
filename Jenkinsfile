pipeline {
  agent any
  options { skipDefaultCheckout(true) }   // avoid the implicit checkout
  environment {
    IMAGE = "tasklist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        // Always get the latest main with a clean workspace
        deleteDir()
        checkout([$class: 'GitSCM',
          branches: [[name: '*/main']],
          doGenerateSubmoduleConfigurations: false,
          extensions: [
            [$class: 'CleanBeforeCheckout'],
            [$class: 'PruneStaleBranch'],
            [$class: 'CloneOption', noTags: false, shallow: false, depth: 0, reference: '', timeout: 20]
          ],
          userRemoteConfigs: [[url: 'https://github.com/ruvxn/SDE-TASK-APP.git']]
        ])
        sh '''
          echo "HEAD: $(git rev-parse HEAD)"
          echo "Tracked tests:"
          git ls-files "tests/**" || true
        '''
      }
    }

    stage('Unit Tests') {
      agent {
        docker {
          image 'python:3.11-slim'
          args '-u 0'   // root in container so pip can install
        }
      }
      steps {
        sh '''
          set -euxo pipefail
          python -V
          pip install --no-cache-dir --upgrade pip
          pip install --no-cache-dir -r requirements.txt pytest
          # Run tests; if none found, print tree to diagnose
          pytest -q --junitxml=pytest-results.xml || (echo "Pytest failed; tree:" && ls -R && exit 1)
        '''
      }
      post {
        always { junit testResults: 'pytest-results.xml', allowEmptyResults: true }
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t $IMAGE .'
      }
    }
  }

  post {
    success { echo 'Level 1 CI pipeline finished successfully.' }
    failure { echo 'Level 1 CI pipeline failed.' }
  }
}
