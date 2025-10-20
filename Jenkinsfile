pipeline {
    agent any

    environment {
        // Docker configuration
        DOCKER_IMAGE = 'taskapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'your-registry-url' // Update with your registry

        // Application configuration
        APP_NAME = 'task-management-app'

        // AWS EC2 configuration
        EC2_HOST = credentials('ec2-host')
        EC2_USER = 'ubuntu'
        SSH_KEY = credentials('ec2-ssh-key')
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
                    pip3 install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running test suite with pytest...'
                sh '''
                    # Set test environment variables
                    export FLASK_ENV=testing
                    export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/project_management_test

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
                    # Install linting tools if not in requirements
                    pip3 install flake8 pylint

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
                echo 'Pushing Docker image to registry...'
                withCredentials([usernamePassword(credentialsId: 'docker-registry-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin ${DOCKER_REGISTRY}
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Deploying to AWS EC2 production server...'
                script {
                    sshagent(credentials: ['ec2-ssh-key']) {
                        sh '''
                            # Copy deployment script to EC2
                            scp -o StrictHostKeyChecking=no deployment/deploy.sh ${EC2_USER}@${EC2_HOST}:/tmp/

                            # Execute deployment on EC2
                            ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'EOF'
                                chmod +x /tmp/deploy.sh
                                /tmp/deploy.sh ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
EOF
                        '''
                    }
                }
            }
        }

        stage('Health Check') {
            when {
                branch 'main'
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Performing health check on deployed application...'
                script {
                    sleep 10 // Wait for application to start
                    sh '''
                        # Check if application is responding
                        curl -f http://${EC2_HOST}:5000/ || exit 1
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            // Send notification (configure as needed)
        }
        failure {
            echo 'Pipeline failed!'
            // Send notification (configure as needed)
        }
        always {
            // Clean up workspace
            cleanWs()

            // Remove dangling Docker images
            sh 'docker image prune -f || true'
        }
    }
}
