# Movie_Review_Sentiment_Analysis

This repository contains a simple web service for sentiment analysis, which includes an AI model developed using scikit-learn  and a Flask web application that serves the model. The deployment is orchestrated using Docker and Kubernetes. The sentiment analysis model predicts whether a given text (such as a movie review) carries a positive or negative sentiment.   review this and tell is it good or bad

## Project Structure

- `app.py`: The main Flask application containing the web service logic.
- `templates/`: Folder containing HTML templates for the web app.
  - `index.html`: Main page for entering movie reviews.
  - `predictions.html`: Page displaying the predictions log.
- `dockerfile`: Dockerfile for creating the Docker image.
- `requirements.txt`: List of Python dependencies.
- `svc.pkl` and `vect.pkl`: Model and vectorizer files saved after training.
- `deployment.yaml`: Kubernetes deployment configuration.
- `service.yaml`: Kubernetes service configuration.

## Setup and Installation

### Prerequisites

- Docker installed on your machine
- Kubernetes cluster configured (you can use Minikube for local testing)
- kubectl installed on your machine

### Running the Web App Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/sentiment-analysis-web-app.git
   ```

2. Navigate to the project folder:

   ```bash
   cd sentiment-analysis-web-app
   ```

3. Build the Docker image:

   ```bash
   docker build -t movie-web-app .
   ```

4. Run the Docker container:

   ```bash
   docker run -p 5000:5000 movie-web-app
   ```

   The web app should be accessible at http://localhost:5000 in your browser.

### Deploying with Kubernetes

1. Apply the Kubernetes deployment and service configurations:

   ```bash
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

2. Monitor the deployment:

   ```bash
   kubectl get pods  # Check pod status
   kubectl get services  # Get the external IP of the service
   ```

   Once the external IP is available, access your application using that IP.


## Cleanup

To delete the Kubernetes deployment and service:

```bash
kubectl delete -f deployment.yaml
kubectl delete -f service.yaml
```

