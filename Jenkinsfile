pipeline {
  agent any

  // Avoid Jenkins' implicit "Declarative: Checkout SCM"
  options { skipDefaultCheckout(true) }

  environment {
    IMAGE = "tasklist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        // Nuke workspace, then do an explicit, clean checkout of latest main
        deleteDir()
        checkout([$class: 'GitSCM',
          branches: [[name: '*/main']],
          doGenerateSubmoduleConfigurations: false,
          extensions: [
            [$class: 'CleanBeforeCheckout'],      // clean workspace before checkout
            [$class: 'PruneStaleBranch'],         // prune stale remote-tracking branches
            [$class: 'CloneOption',
              noTags: false, shallow: false, depth: 0, reference: '', timeout: 20]
          ],
          userRemoteConfigs: [[url: 'https://github.com/ruvxn/SDE-TASK-APP.git']]
        ])

        // Sanity: show commit and any tracked tests found
        sh '''
          echo "HEAD commit: $(git rev-parse HEAD)"
          echo "Tracked tests:"
          git ls-files "tests/**" || true
        '''
      }
    }

    stage('Unit Tests') {
      // Use a Python container so we don't need system Python on the agent
      agent {
        docker {
          image 'python:3.11-slim'
          args '-u 0'  // root inside container so pip can install
        }
      }
      steps {
        sh '''
          set -euxo pipefail
          python -V
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
    success { echo 'Level 1 CI pipeline finished successfully.' }
    failure { echo 'Level 1 CI pipeline failed.' }
  }
}
