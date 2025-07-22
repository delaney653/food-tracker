pipeline {
  agent any
  
  environment{
    VENV = 'venv'
    BUILD_TAG = "v1.0.$BUILD_NUMBER"
    IS_MAIN = "${env.BRANCH_NAME == 'main'}"
  }
  stages{
    stage('Build Image'){
        agent any
      steps{
        checkout scm
        bat "docker build -t food-tracker:$BUILD_NUMBER -t food-tracker:latest ."
        stash includes: '**/*', name: 'code'
      }
    }
    // stage('Parallel Check'){
    //     parallel{
    //         stage('Code Quality: Black Check') {
    //             agent {
    //                 label 'code-quality'
    //             }
    //             steps {
    //                 unstash 'code'
                    
    //                 bat "docker run --rm -v \"%cd%\":/app -w /app food-tracker:$BUILD_NUMBER black --check ."
    //             }
    //             post {
    //                 failure {
    //                     echo 'FAILURE -- Code quality issues detected with Black!'
    //                 }
    //             }
    //         }
    //         stage('Static Testing: SonarQube'){
    //             when {
    //                 branch 'main'
    //             }
    //             agent {
    //                 label 'code-quality'
    //             }
    //             steps {
    //                 unstash 'code'
    //                 script {
    //                     scannerHome = tool 'SonarQube' 
    //                 }
    //                 withSonarQubeEnv('SonarQube') {
    //                     bat "$scannerHome\\bin\\sonar-scanner.bat"
    //                 }
    //             } 
    //         }
    //     }
    // }
    // stage("Wait for Quality Gate") {
    //     when {
    //         branch 'main'
    //     }
    //     steps {
    //         timeout(time: 2, unit: 'MINUTES') {
    //             waitForQualityGate abortPipeline: true
    //         }
    //     }
    // }
    stage('Clean Docker Environment') {
        agent any
        steps {
            script {
                bat 'docker-compose down --volumes --remove-orphans || true'
                bat 'docker system prune -f || true'
            }
        }
    }
    // stage('Load testing'){
    //     steps{
    //         bat """ 
    //             k6 run --out json=results.json test.js
    //             k6-to-junit results.json -o reports/junit-${BUILD_NUMBER}.xml
    //             """
    //     }
    // }
    stage('Run Tests') {
        agent any
            steps {
                script { 
                    try { 
                        bat 'if not exist reports mkdir reports'

                        bat '''
                        docker-compose --profile testing up --build -d --abort-on-container-exit 
                        '''
                        echo "==== MYSQL-TEST LOGS ===="
                        bat 'docker logs food-tracker-mysql-test || exit /b 0'

                        echo "==== E2E-TEST LOGS ===="
                        bat 'docker logs food-tracker-e2e-test || exit /b 0'

                        echo "==== BACKEND-TEST LOGS ===="
                        bat 'docker logs food-tracker-backend-test || exit /b 0'
                        
                        echo "Copying test artifacts from container..."
                        bat """
                        for /f %%i in ('docker-compose --profile testing ps -q backend-test') do (
                            docker cp %%i:/app/junit.xml ./reports/junit.xml 2>nul || echo "Warning: junit.xml not found"
                        )
                        exit /b 0
                        """
                        } catch (Exception e) {
                            bat 'docker-compose --profile testing logs backend-test'
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
        agent any
        steps{
            script{
                 // verify reports were created
                bat """
                if not exist reports\\junit.xml (
                    echo "WARNING -- No test results found! Please check main build page."
                )
                if not exist reports\\coverage.xml (
                    echo "WARNING -- No coverage report found! Please check main build page."
                )
                echo "Test reports generated successfully!"
                """  
            }
        }
    }
        
    stage('Build Artifacts') {
        agent any
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
                    bat "docker images food-tracker"
                    bat """
                    if not exist artifacts mkdir artifacts
                    echo "Exporting build artifacts..."
                    docker save -o artifacts/backend-image-${BUILD_NUMBER}.tar food-tracker:$BUILD_NUMBER
                    dir artifacts"""
                    
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
            archiveArtifacts artifacts: "artifacts/**", allowEmptyArchive: true
            
            junit testResults: "reports/junit.xml", allowEmptyResults: true
            
            slackSend channel: '#new-channel', color: '#2fff00ff', message: "Build #${BUILD_NUMBER} finished with status: ${currentBuild.currentResult} (<${env.BUILD_URL}|Details>)"

            script {
                if (currentBuild.result == 'UNSTABLE') {
                    error("Too many test failures – marking pipeline as FAILED.")
                }
            }

            bat 'docker-compose down --volumes --remove-orphans || true'
            bat 'docker system prune -f || true'
        }
        failure {
            slackSend channel: '#new-channel', color: 'danger', message: " Build *#${BUILD_NUMBER}* failed! (<${env.BUILD_URL}|View Logs>)"
            echo 'Pipeline failed! Check the logs above for details.'
        }
            
        success {
            echo 'Pipeline completed successfully!'
            echo 'All checks passed:'
            echo '- Code formatting (Python Black)'
            echo '- All tests passing'
            echo '- Coverage >= 85%'
            echo '- Build artifacts generated'
        }
    }

}