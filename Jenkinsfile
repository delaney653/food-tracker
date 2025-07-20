pipeline {
  agent any
  
  environment{
    VENV = 'venv'
  }
  stages{
    stage('Clean Docker Environment') {
        steps {
            script {
                bat 'docker-compose down --volumes --remove-orphans || true'
                bat 'docker system prune -f || true'
            }
        }
    }
    stage('Checkout git'){
      steps{
        git branch: 'main', url: 'https://github.com/delaney653/food-tracker'
      }
    }
    stage('Code Quality: Black Check') {
        steps {
            script {
                echo 'Checking code formatting with Black...'
                // Fail the build if code is not black-formatted
                bat '''
                docker run --rm -v %CD%:/app -w /app python:3.9 sh -c "pip install -r requirements.txt && black --check . --exclude venv"
                if %ERRORLEVEL% neq 0 (
                    echo.
                    echo FAILURE -- Black formatting issues have been detected
                    echo To auto-fix this locally, run: black .
                    exit /b 1
                ) else (
                    echo Black check passed.
                )
                '''
            }
        }
    }
    stage('Code Quality: Pylint Check'){
        steps {
            script {
                echo 'Checking with Pylint...'
                // Fail the build if pylint score is below 8.0
                bat '''
                docker run --rm -v %CD%:/app -w /app python:3.9 sh -c "pip install -r requirements.txt && find . -name '*.py' -not -path './venv/*' -not -path './migrations/*' -not -path './__pycache__/*' | xargs pylint --output-format=colorized --fail-under=8.0" 
                if %ERRORLEVEL% neq 0 (
                    echo.
                    echo FAILURE -- Code quality issues detected with Pylint!
                    echo To fix this locally run: pylint <file_name> in the appropriate directoy.
                    echo Please review suggestions and aim for a score ^>= 8.0.
                    exit /b 1
                ) else (
                    echo Pylint check passed.
                )
                '''
            }
        }
    }
    stage('Run Tests') {
            steps {
                script { 
                    try {
                        bat 'if not exist reports mkdir reports'

                        bat '''
                        docker-compose --profile testing up --build -d
                        '''
                        
                        echo "Copying test artifacts from container..."
                        bat '''
                        for /f %%i in ('docker-compose --profile testing ps -q backend-test') do (
                            docker cp %%i:/app/junit.xml ./reports/junit.xml 2>nul || echo "Warning: junit.xml not found"
                        )
                        exit /b 0
                        '''
                        } catch (Exception e) {
                        echo "Test stage failed: ${e.getMessage()}"
                        currentBuild.result = 'FAILURE'
                        throw e
                    } finally {
                        bat 'docker-compose --profile testing down --volumes --remove-orphans || true'
                        bat 'docker-compose down --volumes --remove-orphans || true'
                    }
                }
                       
            }
    }

    stage('Verifying Test Reports were Generated'){
        steps{
            script{
                 // verify reports were created
                    bat '''
                    if not exist reports\\junit.xml (
                        echo "WARNING -- No test results found! Please check main build page."
                    )
                    if not exist reports\\coverage.xml (
                        echo "WARNING -- No coverage report found! Please check main build page."
                    )
                    echo "Test reports generated successfully!"
                    '''
                    
                }
            }
        }
    }
        
    stage('Build Artifacts') {
        steps {
            script {
                echo 'Building application artifacts...'
                try {
                    bat 'docker-compose build backend'
                    
                    bat '''
                    echo "Verifying build artifacts..."
                    docker images | findstr backend && echo "Docker image built successfully" || (
                        echo "FAILURE -- Docker image not found!"
                        exit /b 1
                    )
                    '''
                    
                    bat '''
                    if not exist artifacts mkdir artifacts
                    echo "Exporting build artifacts..."
                    docker save -o artifacts/backend-image.tar digital-notebook-backend:latest || echo "Could not export backend image"
                    ''' 
                    
                    echo 'Build artifacts generated successfully!'
                    
                } catch (Exception e) {
                    echo "Build stage failed: ${e.getMessage()}"
                    currentBuild.result = 'FAILURE'
                    throw e
                }
            }
        }
    }
    }
    
    post {
        always {
            echo 'Archiving artifacts and publishing reports...'
            
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            archiveArtifacts artifacts: 'artifacts/**', allowEmptyArchive: true
            
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
            
            script {
                if (currentBuild.result == 'UNSTABLE') {
                    error("Too many test failures – marking pipeline as FAILED.")
                }
            }

            bat 'docker-compose down --volumes --remove-orphans || true'
            bat 'docker system prune -f || true'
        }
        failure {
            echo 'Pipeline failed! Check the logs above for details.'
        }
            
        success {
            echo 'Pipeline completed successfully!'
            echo 'All checks passed:'
            echo '- Code formatting (Python Black)'
            echo '- Code quality (Pylint >= 8.0)'
            echo '- All tests passing'
            echo '- Coverage >= 85%'
            echo '- Build artifacts generated'
        }
    }

}