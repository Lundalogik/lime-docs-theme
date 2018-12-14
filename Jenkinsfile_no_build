pipeline {
    agent { label 'linux' }

    options {
        disableConcurrentBuilds()
    }

    triggers {
        cron('H 17 * * *')
    }

    stages {
        stage('Build and test') {
            steps {
                sh 'make test'
            }
        }

        stage('Publish package') {
            environment {
                DEVPI_CREDENTIALS = credentials('devpi-login')
            }
            steps {
                sshagent(['663e4b49-30f6-4c46-a018-a37ba604d7c8']) {
                    script {
                        def output = sh(returnStdout: true, script:'DEVPI_USERNAME=$DEVPI_CREDENTIALS_USR DEVPI_PASSWORD=$DEVPI_CREDENTIALS_PSW make publish').trim()
                            echo(output)
                            def match = output =~ /Published to pypi: (.*)==(.*)/
                            if(match) {
                                def package_name = match.group(1)
                                    def package_version = match.group(2)

                                    // Set match to null to prevent Jenkins from attempting to serialize it
                                    // before shelling out. This will fail since the matcher isn't serializable.
                                    match = null

                                    sh("git tag --annotate --message 'Version ${package_version}' v${package_version}")
                                    sh("git push origin v${package_version}")

                                    build(job: 'python-package-published', parameters: [string(name: 'package_name', value: package_name), string(name: 'package_version', value: package_version)], wait: false)
                            } else {
                                echo('This version of the package has already been published.')
                            }
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                if (env.BRANCH_NAME == 'master') {
                    slackSend(baseUrl: 'https://lime-technologies.slack.com/services/hooks/jenkins-ci/',
                              botUser: true,
                              channel: '#crm-build',
                              color: 'good',
                              message: "Job ${JOB_NAME} on node ${NODE_NAME} finished successfully. ${BUILD_URL}",
                              tokenCredentialId: 'slack-token')
                }
            }
        }

        failure {
            script {
                if (env.BRANCH_NAME == 'master') {
                    slackSend(baseUrl: 'https://lime-technologies.slack.com/services/hooks/jenkins-ci/',
                              botUser: true,
                              channel: '#crm-build',
                              color: 'danger',
                              message: "Job ${JOB_NAME} on node ${NODE_NAME} failed. ${BUILD_URL}",
                              tokenCredentialId: 'slack-token')
                }
            }
        }
    }
}
