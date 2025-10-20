pipeline {
  agent any
  options { skipDefaultCheckout(true) }

  environment {
    IMAGE = "tasklist-app:build-${env.BUILD_NUMBER}"   // safe tag
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
          echo "Tracked tests:"; git ls-files "tests/**" || true
          ls -la | sed -n '1,120p'
        '''
      }
    }

    stage('Unit Tests') {
      agent {
        docker {
          image 'python:3.11-slim'
          args '-u 0'
          reuseNode true
        }
      }
      steps {
        sh '''
          set -euxo pipefail
          export PYTHONPATH="$PWD"     # allow `import run`
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
        sh '''
          set -euxo pipefail
          test -f Dockerfile || (echo "Missing Dockerfile at repo root"; ls -la; exit 1)
          docker build -t "$IMAGE" .
        '''
      }
    }
  }

  post {
    success { echo 'Level 1 CI pipeline finished successfully.' }
    failure { echo 'Level 1 CI pipeline failed.' }
  }
}
