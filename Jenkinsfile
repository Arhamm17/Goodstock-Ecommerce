pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        DOCKERHUB_NAMESPACE = 'YOUR_DOCKERHUB_USERNAME'

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

        stage('Build Images') {
            steps {
                sh '''
                    set -eux

                    docker build \
                      -t ${API_GATEWAY_IMAGE}:${IMAGE_TAG} \
                      ./api-gateway

                    docker build \
                      -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                      ./frontend-gateway

                    docker build \
                      -t ${PRODUCT_IMAGE}:${IMAGE_TAG} \
                      ./product-service

                    docker build \
                      -t ${ORDER_IMAGE}:${IMAGE_TAG} \
                      ./order-service

                    docker build \
                      -t ${USER_IMAGE}:${IMAGE_TAG} \
                      ./user-service
                '''
            }
        }

        stage('Push Images') {
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

                        docker push ${API_GATEWAY_IMAGE}:${IMAGE_TAG}
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                        docker push ${PRODUCT_IMAGE}:${IMAGE_TAG}
                        docker push ${ORDER_IMAGE}:${IMAGE_TAG}
                        docker push ${USER_IMAGE}:${IMAGE_TAG}

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                sh '''
                    set -eux

                    kubectl set image \
                      deployment/api-gateway \
                      api-gateway=${API_GATEWAY_IMAGE}:${IMAGE_TAG} \
                      -n ${K8S_NAMESPACE}

                    kubectl set image \
                      deployment/frontend-gateway \
                      frontend-gateway=${FRONTEND_IMAGE}:${IMAGE_TAG} \
                      -n ${K8S_NAMESPACE}

                    kubectl set image \
                      deployment/product-service \
                      product-service=${PRODUCT_IMAGE}:${IMAGE_TAG} \
                      -n ${K8S_NAMESPACE}

                    kubectl set image \
                      deployment/order-service \
                      order-service=${ORDER_IMAGE}:${IMAGE_TAG} \
                      -n ${K8S_NAMESPACE}

                    kubectl set image \
                      deployment/user-service \
                      user-service=${USER_IMAGE}:${IMAGE_TAG} \
                      -n ${K8S_NAMESPACE}
                '''
            }
        }

        stage('Verify Rollouts') {
            steps {
                sh '''
                    set -eux

                    kubectl rollout status deployment/api-gateway \
                      -n ${K8S_NAMESPACE} --timeout=180s

                    kubectl rollout status deployment/frontend-gateway \
                      -n ${K8S_NAMESPACE} --timeout=180s

                    kubectl rollout status deployment/product-service \
                      -n ${K8S_NAMESPACE} --timeout=180s

                    kubectl rollout status deployment/order-service \
                      -n ${K8S_NAMESPACE} --timeout=180s

                    kubectl rollout status deployment/user-service \
                      -n ${K8S_NAMESPACE} --timeout=180s
                '''
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
                    echo "Deployed tag: ${IMAGE_TAG}"

                    kubectl get deployments \
                      -n ${K8S_NAMESPACE}

                    kubectl get pods \
                      -n ${K8S_NAMESPACE}
                '''
            }
        }
    }

    post {
        success {
            echo "CI/CD deployment successful."
            echo "Image tag: ${env.IMAGE_TAG}"
        }

        failure {
            echo "Pipeline failed. Collecting Kubernetes diagnostics."

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