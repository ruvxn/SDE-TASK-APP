pipeline {
  agent any
  options { skipDefaultCheckout(true) }

  environment {
    IMAGE = "tasklist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
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
          args '-u 0'
          reuseNode true        // <— use SAME workspace instead of tasklist-ci@2
        }
      }
      steps {
        sh '''
          set -euxo pipefail
          echo "PWD: $(pwd)"
          ls -la
          [ -d tests ] && ls -la tests || true

          python -V
          pip install --no-cache-dir --upgrade pip
          pip install --no-cache-dir -r requirements.txt pytest
          pytest -q --junitxml=pytest-results.xml
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
