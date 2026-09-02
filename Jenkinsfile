pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        DOCKERHUB_NAMESPACE = 'arhammrashid17'

        API_GATEWAY_IMAGE = "${arhammrashid17}/devops-ecommerce-api-gateway"
        FRONTEND_IMAGE    = "${arhammrashid17}/devops-ecommerce-frontend"
        PRODUCT_IMAGE     = "${arhammrashid17}/devops-ecommerce-product"
        ORDER_IMAGE       = "${arhammrashid17}/devops-ecommerce-order"
        USER_IMAGE        = "${arhammrashid17}/devops-ecommerce-user"

        KUBECONFIG    = '/var/lib/jenkins/.kube/config'
        K8S_NAMESPACE = 'devops-ecommerce'

    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Initialize') {
            steps {
                script {
                    def shortCommit = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${shortCommit}"

                    echo "Image tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Detect Changes') {
    steps {
        script {

            if (!env.GIT_PREVIOUS_SUCCESSFUL_COMMIT?.trim()) {

                echo 'No previous successful Jenkins commit found.'
                echo 'Building all application images.'

                env.API_GATEWAY_CHANGED = 'true'
                env.FRONTEND_CHANGED    = 'true'
                env.PRODUCT_CHANGED     = 'true'
                env.ORDER_CHANGED       = 'true'
                env.USER_CHANGED        = 'true'

            } else {

                sh """
                    git diff --name-only \
                      ${env.GIT_PREVIOUS_SUCCESSFUL_COMMIT} \
                      ${env.GIT_COMMIT} \
                      > changed-files.txt
                """

                sh '''
                    echo "Changed files:"
                    if [ -s changed-files.txt ]; then
                        cat changed-files.txt
                    else
                        echo "No changed files detected"
                    fi
                '''

                env.API_GATEWAY_CHANGED = sh(
                    script: """
                        if grep -q '^api-gateway/' changed-files.txt; then
                            echo true
                        else
                            echo false
                        fi
                    """,
                    returnStdout: true
                ).trim()

                env.FRONTEND_CHANGED = sh(
                    script: """
                        if grep -q '^frontend-gateway/' changed-files.txt; then
                            echo true
                        else
                            echo false
                        fi
                    """,
                    returnStdout: true
                ).trim()

                env.PRODUCT_CHANGED = sh(
                    script: """
                        if grep -q '^product-service/' changed-files.txt; then
                            echo true
                        else
                            echo false
                        fi
                    """,
                    returnStdout: true
                ).trim()

                env.ORDER_CHANGED = sh(
                    script: """
                        if grep -q '^order-service/' changed-files.txt; then
                            echo true
                        else
                            echo false
                        fi
                    """,
                    returnStdout: true
                ).trim()

                env.USER_CHANGED = sh(
                    script: """
                        if grep -q '^user-service/' changed-files.txt; then
                            echo true
                        else
                            echo false
                        fi
                    """,
                    returnStdout: true
                ).trim()
            }

            echo """
                Change detection result:
                --------------------------------
                API Gateway : ${env.API_GATEWAY_CHANGED}
                Frontend    : ${env.FRONTEND_CHANGED}
                Product     : ${env.PRODUCT_CHANGED}
                Order       : ${env.ORDER_CHANGED}
                User        : ${env.USER_CHANGED}
                --------------------------------
                """
                    }
                }
            }

        stage('Validate') {
            steps {
                sh '''
                    set -eux

                    git diff --check

                    test -f api-gateway/Dockerfile
                    test -f frontend-gateway/Dockerfile
                    test -f product-service/Dockerfile
                    test -f order-service/Dockerfile
                    test -f user-service/Dockerfile

                    docker --version
                    kubectl get namespace ${K8S_NAMESPACE}
                '''
            }
        }

        stage('Build API Gateway') {
            when {
                expression {
                    env.API_GATEWAY_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    docker build \
                      -t ${API_GATEWAY_IMAGE}:${IMAGE_TAG} \
                      ./api-gateway
                '''
            }
        }

        stage('Build Frontend') {
            when {
                expression {
                    env.FRONTEND_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    docker build \
                      -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                      ./frontend-gateway
                '''
            }
        }

        stage('Build Product Service') {
            when {
                expression {
                    env.PRODUCT_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    docker build \
                      -t ${PRODUCT_IMAGE}:${IMAGE_TAG} \
                      ./product-service
                '''
            }
        }

        stage('Build Order Service') {
            when {
                expression {
                    env.ORDER_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    docker build \
                      -t ${ORDER_IMAGE}:${IMAGE_TAG} \
                      ./order-service
                '''
            }
        }

        stage('Build User Service') {
            when {
                expression {
                    env.USER_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    docker build \
                      -t ${USER_IMAGE}:${IMAGE_TAG} \
                      ./user-service
                '''
            }
        }

        stage('Push Images') {

            when {
                expression {
                    env.API_GATEWAY_CHANGED == 'true' ||
                    env.FRONTEND_CHANGED == 'true' ||
                    env.PRODUCT_CHANGED == 'true' ||
                    env.ORDER_CHANGED == 'true' ||
                    env.USER_CHANGED == 'true'
                }
            }

            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {

                    sh '''
                        set +x

                        echo "$DOCKERHUB_TOKEN" | \
                          docker login \
                          -u "$DOCKERHUB_USER" \
                          --password-stdin

                        set -x
                    '''

                    script {

                        if (env.API_GATEWAY_CHANGED == 'true') {
                            sh '''
                                docker push \
                                  ${API_GATEWAY_IMAGE}:${IMAGE_TAG}
                            '''
                        }

                        if (env.FRONTEND_CHANGED == 'true') {
                            sh '''
                                docker push \
                                  ${FRONTEND_IMAGE}:${IMAGE_TAG}
                            '''
                        }

                        if (env.PRODUCT_CHANGED == 'true') {
                            sh '''
                                docker push \
                                  ${PRODUCT_IMAGE}:${IMAGE_TAG}
                            '''
                        }

                        if (env.ORDER_CHANGED == 'true') {
                            sh '''
                                docker push \
                                  ${ORDER_IMAGE}:${IMAGE_TAG}
                            '''
                        }

                        if (env.USER_CHANGED == 'true') {
                            sh '''
                                docker push \
                                  ${USER_IMAGE}:${IMAGE_TAG}
                            '''
                        }
                    }

                    sh 'docker logout'
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                script {

                    if (env.API_GATEWAY_CHANGED == 'true') {
                        sh '''
                            kubectl set image \
                              deployment/api-gateway \
                              api-gateway=${API_GATEWAY_IMAGE}:${IMAGE_TAG} \
                              -n ${K8S_NAMESPACE}
                        '''
                    }

                    if (env.FRONTEND_CHANGED == 'true') {
                        sh '''
                            kubectl set image \
                              deployment/frontend-gateway \
                              frontend-gateway=${FRONTEND_IMAGE}:${IMAGE_TAG} \
                              -n ${K8S_NAMESPACE}
                        '''
                    }

                    if (env.PRODUCT_CHANGED == 'true') {
                        sh '''
                            kubectl set image \
                              deployment/product-service \
                              product-service=${PRODUCT_IMAGE}:${IMAGE_TAG} \
                              -n ${K8S_NAMESPACE}
                        '''
                    }

                    if (env.ORDER_CHANGED == 'true') {
                        sh '''
                            kubectl set image \
                              deployment/order-service \
                              order-service=${ORDER_IMAGE}:${IMAGE_TAG} \
                              -n ${K8S_NAMESPACE}
                        '''
                    }

                    if (env.USER_CHANGED == 'true') {
                        sh '''
                            kubectl set image \
                              deployment/user-service \
                              user-service=${USER_IMAGE}:${IMAGE_TAG} \
                              -n ${K8S_NAMESPACE}
                        '''
                    }
                }
            }
        }

        stage('Verify Rollouts') {
            steps {
                script {

                    if (env.API_GATEWAY_CHANGED == 'true') {
                        sh '''
                            kubectl rollout status \
                              deployment/api-gateway \
                              -n ${K8S_NAMESPACE} \
                              --timeout=180s
                        '''
                    }

                    if (env.FRONTEND_CHANGED == 'true') {
                        sh '''
                            kubectl rollout status \
                              deployment/frontend-gateway \
                              -n ${K8S_NAMESPACE} \
                              --timeout=180s
                        '''
                    }

                    if (env.PRODUCT_CHANGED == 'true') {
                        sh '''
                            kubectl rollout status \
                              deployment/product-service \
                              -n ${K8S_NAMESPACE} \
                              --timeout=180s
                        '''
                    }

                    if (env.ORDER_CHANGED == 'true') {
                        sh '''
                            kubectl rollout status \
                              deployment/order-service \
                              -n ${K8S_NAMESPACE} \
                              --timeout=180s
                        '''
                    }

                    if (env.USER_CHANGED == 'true') {
                        sh '''
                            kubectl rollout status \
                              deployment/user-service \
                              -n ${K8S_NAMESPACE} \
                              --timeout=180s
                        '''
                    }
                }
            }
        }

        stage('Smoke Tests') {
            steps {
                sh '''
                    set -eux

                    curl --fail \
                      --retry 5 \
                      --retry-delay 3 \
                      --max-time 10 \
                      http://localhost:30080/health

                    curl --fail \
                      --retry 3 \
                      --max-time 10 \
                      http://localhost:30080/api/products

                    curl --fail \
                      --retry 3 \
                      --max-time 10 \
                      http://localhost:30080/api/orders
                '''
            }
        }

        stage('Deployment Summary') {
            steps {
                sh '''
                    echo "Pipeline image tag: ${IMAGE_TAG}"

                    kubectl get deployments \
                      -n ${K8S_NAMESPACE} \
                      -o custom-columns='NAME:.metadata.name,IMAGE:.spec.template.spec.containers[*].image'

                    kubectl get pods \
                      -n ${K8S_NAMESPACE}
                '''
            }
        }
    }

    post {

        success {
            echo 'CI/CD pipeline completed successfully.'
            echo "Pipeline image tag: ${env.IMAGE_TAG}"
        }

        failure {
            echo 'Pipeline failed. Collecting Kubernetes diagnostics.'

            sh '''
                kubectl get pods \
                  -n ${K8S_NAMESPACE} \
                  -o wide || true

                kubectl get events \
                  -n ${K8S_NAMESPACE} \
                  --sort-by=.lastTimestamp \
                  | tail -40 || true
            '''
        }

        always {
            sh '''
                docker image prune -f || true
            '''
        }
    }
}