# Post Management API
## Overview
The Post Management API is a backend application built using FastAPI, Pydantic, and SQLAlchemy. It offers functionality for managing posts and comments, user authentication and registration with JWT, and analytics on user comments. The project also integrates with Vertex AI for automatic responses to comments.

## Features
- CRUD operations for posts and comments.
- JWT-based user authentication and registration.
- Vertex AI Integration for automatic replies to comments.
- Comment analytics providing daily breakdown of comments and blocked comments.
- API Documentation accessible at /docs/.
## Environment Setup
Create a .env file in the project root and add the following environment variables:


```
SECRET_KEY=your_secret_key_for_password_hashing
GCLOUD_PROJECT_ID=your_vertexai_project_id
API_NINJAS_KEY=your_api_ninjas_key
```
### Instructions for Generating Keys:
- SECRET_KEY: You can generate a secure key using the following command in Python:

```bash
import secrets
print(secrets.token_hex(32))
```
- GCLOUD_PROJECT_ID: The project ID for your Google Cloud Vertex AI project.

- API_NINJAS_KEY: API key obtained from the API Ninjas website for checking comments for harmful language.

## Setup and Run the Project
### Prerequisites
- Python 3.8+
- Google Cloud SDK (if integrating with Vertex AI)
- Poetry or other package management tool
### Steps
1. Clone the Repository:

```bash
git clone https://github.com/SuskyiVolodymyr/post-management-api.git
cd post-management-api
```
2. Install Dependencies:

```bash
pip install -r requirements.txt
```
3. Set Up Environment Variables:

Ensure your .env file is in the root directory of your project.

4. Migrate the Database:

```bash
alembic upgrade head
```
5. Run the Project:

```bash
python -m uvicorn main:app --reload
```
6. Authenticate with Google Cloud (for Vertex AI):

```bash
gcloud auth application-default login
```
7. View the API Documentation:

Navigate to http://127.0.0.1:8000/docs/ to explore all the endpoints and test them using Swagger UI.

## Authentication
The API uses JWT tokens for authentication. To get started:

1. Register a New User: Send a POST request to /register/ with your email and password.
2. Get a Token: Send a POST request to /token/ with the registered email and password to receive an access token.
3. Use the Token: Include the token in the Authorization header as Bearer <your_token> for all authenticated routes.
## API Endpoints
### Posts
- POST /posts/ - Create a new post.
- GET /posts/ - Get a list of all posts.
- GET /posts/{post_id}/ - Get a post by its ID.
- PUT /posts/{post_id}/ - Update a post.
- DELETE /posts/{post_id}/ - Delete a post.
### Comments
- POST /comments/ - Create a new comment.
- GET /comments/ - Get a list of all comments. You can provide a post_id parameter to filter comments by a specific post.
- GET /comments/{comment_id}/ - Get a comment by its ID.
- PUT /comments/{comment_id}/ - Update a comment.
- DELETE /comments/{comment_id}/ - Delete a comment.
### Comment Analytics
- GET /comments-daily-breakdown/ - Get a breakdown of comments created and blocked per day between two dates.
## Vertex AI Integration
The project leverages Google Cloud’s Vertex AI to automatically generate replies to user comments based on the context of the post. To use this feature, ensure you are authenticated with Google Cloud:

1. Authenticate with Google Cloud:

```bash
gcloud auth application-default login
```
Ensure you have set up the necessary environment variables in .env.

## Additional Information
- Technology Stack: FastAPI, Pydantic, SQLAlchemy, Vertex AI, JWT
- Testing: Use Pytest to execute tests.
```bash
pytest 
```