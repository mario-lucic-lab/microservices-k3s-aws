Migration of an AI Application from a Monolith to Microservices

Architecture & Migration: Unlike a monolithic architecture where all functionalities are coupled into a single unit, microservices operate as independent services within their own containers inside Kubernetes pods, ensuring fault isolation, easier maintenance, and independent scaling without affecting the rest of the system.

AI Classification Microservice (ai-service): Uses a pre-trained Logistic Regression model (model.pkl) saved via Python's pickle module and trained on news headlines and short descriptions from the Kaggle News Category dataset. Text is preprocessed (stop-word removal, diacritic replacement, lemmatization) and converted into vectors using TF-IDF, while label_encoder.pkl maps numerical predictions (0–41) to category names via a FastAPI /predict endpoint on port 8000 alongside health-check routes.

Gemini Microservice: Built with FastAPI (ai_backend.py) on port 8001 with /predict, /analyze, and health-check routes. It uses the Gemini LLM API and prompt engineering to analyze news content, extract key elements, translate articles into Croatian, and recommend related news, with the API key securely passed via Kubernetes Secrets.

Frontend Microservice: Served via an Nginx Docker image (index.html and gemini.html), providing the user interface, dynamically resolving API addresses using window.location.origin, and polling the health-check endpoints of both AI services every 60 seconds.

Infrastructure & DevOps: Terraform automates the creation of 3 AWS instances (one t3.small master node with an Elastic IP and two t3.micro worker nodes), swap memory, and security groups (SSH port 22 restricted to admin IP, internal cluster traffic allowed, HTTP port 80 open). Services are packaged with Docker, stored on Docker Hub, tested locally with Docker Compose, orchestrated with K3s YAML manifests, routed through the Traefik Ingress Controller (main-ingress.yaml), and monitored via AWS CloudWatch.

Demonstrated Scenarios: The deployment demonstrates zero-downtime service replacement by redirecting /predict traffic from the classical AI service (:8000) to the Gemini service (:8001) in main-ingress.yaml, automatic pod recovery (self-healing) after a simulated pod failure, and horizontal scaling across worker nodes to distribute load and reduce response times.
