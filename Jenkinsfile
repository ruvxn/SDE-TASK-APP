pipeline {
    agent any

    environment {
        // Docker configuration
        DOCKER_IMAGE = 'taskapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'docker.io' // Default to Docker Hub

        // Application configuration
        APP_NAME = 'task-management-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
                sh 'git log -1 --pretty=format:"%h - %an, %ar : %s"'
            }
        }

        stage('Environment Setup') {
            steps {
                echo 'Setting up environment...'
                sh '''
                    python3 --version
                    pip3 --version
                    docker --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    # Create virtual environment
                    python3 -m venv venv

                    # Activate and install dependencies
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running test suite with pytest...'
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate

                    # Set test environment variables
                    export FLASK_ENV=testing
                    export DATABASE_URL=sqlite:///:memory:

                    # Run tests with coverage
                    pytest tests/ -v --cov=. --cov-report=html --cov-report=xml --cov-report=term-missing
                '''
            }
            post {
                always {
                    // Archive test results
                    junit(allowEmptyResults: true, testResults: '**/test-results/*.xml')

                    // Publish coverage report
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
                failure {
                    echo 'Tests failed! Build will not proceed.'
                }
            }
        }

        stage('Code Quality Check') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate

                    # Install linting tools if not in requirements
                    pip install flake8 pylint

                    # Run flake8 (allow failures, just report)
                    flake8 . --exclude=venv,ENV --max-line-length=120 --count --statistics || true
                '''
            }
        }

        stage('Build Docker Image') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Push to Registry') {
            when {
                branch 'main'
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Skipping push to registry - configure docker-registry-creds to enable'
                echo 'Docker image built locally: ${DOCKER_IMAGE}:${DOCKER_TAG}'
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Skipping deployment - configure EC2 credentials to enable'
                echo 'To enable deployment:'
                echo '1. Add ec2-host credential in Jenkins'
                echo '2. Add ec2-ssh-key credential in Jenkins'
                echo '3. Uncomment deployment code in Jenkinsfile'
            }
        }

        stage('Health Check') {
            when {
                branch 'main'
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Skipping health check - no deployment configured'
                echo 'Local health check - Docker image ready for deployment'
            }
        }
    }

    post {
        success {
            echo '========================================='
            echo 'Pipeline completed successfully!'
            echo '========================================='
            echo "Build: #${BUILD_NUMBER}"
            echo "Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
            echo '========================================='
        }
        failure {
            echo '========================================='
            echo 'Pipeline failed!'
            echo '========================================='
            echo 'Check the logs above for details'
            echo '========================================='
        }
        always {
            echo 'Cleaning up...'
            // Remove dangling Docker images
            sh 'docker image prune -f || true'
        }
    }
}
