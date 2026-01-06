# Software Engineer Challenge
## Overview
Welcome to the Software Engineer Application Challenge. In this challenge, you will demonstrate your skills in backend development, API design, testing, and cloud deployment.

## Problem
You will develop a RESTful API for user management with complete CRUD (Create, Read, Update, Delete) operations. The application should handle user data with the following attributes:

| Field       | Description                              |
|-------------|------------------------------------------|
| id          | Unique identifier for each user          |
| username    | User's unique username                   |
| email       | User's email address                     |
| first_name  | User's first name                        |
| last_name   | User's last name                         |
| role        | User role (admin, user, guest)           |
| created_at  | Timestamp when the user was created      |
| updated_at  | Timestamp when the user was last updated |
| active      | Boolean indicating if the user is active |

## Challenge

### Context:
In today's digital landscape, effective user management is a foundational component of virtually all software applications. This challenge simulates a real-world scenario where a user management API is needed for a growing application.

As a Software Engineer, you've been tasked with building a robust and scalable user management API that will serve as the backbone for user-related operations. The API should provide a clean interface for creating, retrieving, updating, and deleting user profiles while ensuring data integrity and following industry best practices.

Beyond just functionality, we're interested in seeing your approach to software architecture, code organization, testing strategies, and cloud deployment skills. This challenge is designed to showcase not only your technical abilities but also your understanding of production-ready software development.


### API Development
Develop an API with FastAPI:

- Implement all CRUD endpoints for user management
- Add proper input validation for all requests
- Document all endpoints using OpenAPI/Swagger
- Implement proper error handling for edge cases
- The API should connect to a database of your choice (SQL or NoSQL)
- Write detailed API tests using pytest
- Deploy your API to Google Cloud Platform (GCP)

Requirements:
- You must use FastAPI as the framework
- Provide examples of API calls for each endpoint in your documentation
- Write clean, maintainable code with proper comments
- The API should follow REST best practices
- Include at least basic logging functionality
- Create a `cloudbuild.yaml` file for Google Cloud Build that includes:
  - Building the Docker image
  - Running tests
  - Deploying the application to Google Cloud Run or App Engine

### Evaluation Criteria
Your submission will be evaluated based on the following criteria:

- **Code Quality**: Readability, organization, and adherence to Python best practices
- **API Design**: Proper implementation of RESTful principles and resource modeling
- **Data Handling**: Effective data validation, error handling, and database integration
- **Testing**: Comprehensive test coverage and proper test organization
- **Documentation**: Clear and complete API documentation
- **Cloud Deployment**: Successful deployment to GCP and proper configuration
- **CI/CD Implementation**: Quality and completeness of the `cloudbuild.yaml` file
- **Overall Functionality**: The API works as expected for all CRUD operations

### Submission Instructions
To submit your challenge, you must do a POST request to: https://advana-challenge-check-api-cr-k4hdbggvoq-uc.a.run.app/software-engineer

This is an example of the body you must send:

```json
{
  "name": "Juan Perez",
  "mail": "juan.perez@example.com",
  "github_url": "https://github.com/juanperez/se-challenge.git",
  "api_url": "https://juan-perez.api"
}
```

PLEASE, SEND THE REQUEST ONLY ONCE.
If your request was successful, you will receive this message:

```
jsonCopiar{
  "status": "OK",
  "detail": "your request was received"
}
```

NOTE: We recommend sending the challenge even if you didn't manage to finish all the parts.