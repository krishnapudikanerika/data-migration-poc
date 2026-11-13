pipeline {
    agent any

    environment {
        PYTHON_EXE = "C:\\Users\\1831\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
    }

    stages {
        stage('Setup Python Environment') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            "%PYTHON_EXE%" -m venv venv
                            call venv\\Scripts\\activate
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Run Data Migration Validation') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            pytest -v --html=reports/management_demo_report.html --self-contained-html --junitxml=reports/junit_results.xml
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate
                            pytest -v --html=reports/management_demo_report.html --self-contained-html --junitxml=reports/junit_results.xml
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            // 1. Archive standalone text diff logs & HTML report as build artifacts
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true

            // 2. Publish JUnit XML so Jenkins shows native Pass/Fail test trends
            junit allowEmptyResults: true, testResults: 'reports/junit_results.xml'

            // 3. Publish interactive HTML report inside Jenkins UI (Requires HTML Publisher Plugin)
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'management_demo_report.html',
                reportName: 'Data Migration Executive Report'
            ])
        }
    }
}
