# TaskConsumer WebSocket and API Endpoints Usage Documentation

This documentation provides instructions for frontend developers on how to use the `TaskConsumer` WebSocket class for managing tasks in a Django Channels application and accessing various API endpoints.

## Installation

### Setup Environment

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create a Virtual Environment**:
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply Migrations**:
    ```bash
    python manage.py migrate
    ```

5. **Run the Local Server**:
    ```bash
    python manage.py runserver
    ```

### Additional Setup for Channels

1. **Run Redis with Docker**:
    Ensure you have Docker installed, then run the following command to start a Redis container:
    ```bash
    docker run -d -p 6379:6379 redis
    ```

2. **Update Django Settings**:
    Ensure your `settings.py` includes the necessary configurations for Channels and Redis:
    ```python
    INSTALLED_APPS = [
        # other apps
        'channels',
    ]

    ASGI_APPLICATION = 'your_project_name.asgi.application'
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('127.0.0.1', 6379)],
            },
        },
    }
    ```

## WebSocket URL

The WebSocket URL for connecting to the `TaskConsumer` is:
```
ws://localhost:8000/ws/tasks/
```

## WebSocket Authentication

The first message after connecting must be an authentication message containing a valid JWT token.

### Authentication Message Format

```json
{
    "type": "auth",
    "token": "<JWT_TOKEN>"
}
```

## Task Operations

After authentication, you can perform various task operations by sending messages with the appropriate mode.

### Message Format

#### Retrieve All Tasks

```json
{
    "mode": "all"
}
```

#### Create a Task

```json
{
    "mode": "create",
    "data": {
        "task": "Task name",
        "description": "Task description"
    }
}
```

#### Read a Specific Task

```json
{
    "mode": "read",
    "task_id": "<TASK_UUID>"
}
```

#### Update a Task

```json
{
    "mode": "update",
    "task_id": "<TASK_UUID>",
    "data": {
        "task": "Updated task name",
        "description": "Updated task description"
    }
}
```

#### Delete a Task

```json
{
    "mode": "delete",
    "task_id": "<TASK_UUID>"
}
```

## Example Frontend Usage

Here is an example of how a frontend developer can use the WebSocket connection with this consumer using JavaScript:

### Connecting to WebSocket and Authenticating

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/tasks/');

// On connection open
socket.onopen = function(event) {
    // Authenticate with JWT token
    const authMessage = JSON.stringify({
        type: 'auth',
        token: 'your_jwt_token_here'
    });
    socket.send(authMessage);
};

// On receiving a message
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message from server:', data);
};

// Handling socket close
socket.onclose = function(event) {
    console.log('WebSocket is closed now.', event);
};

// Handling socket errors
socket.onerror = function(error) {
    console.log('WebSocket error:', error);
};
```

## API Endpoints

### URL Patterns

- **Task List and Create**: `GET` and `POST`
    ```
    / (TaskListCreate)
    ```

- **Task Retrieve, Update, and Destroy**: `GET`, `PUT`, `PATCH`, `DELETE`
    ```
    /task/<str:pk>/ (TaskRetrieveUpdateDestroy)
    ```

- **Token Refresh**: `POST`
    ```
    /token-refresh/ (TokenRefreshView)
    ```

- **Login (Obtain JWT Token)**: `POST`
    ```
    /login/ (TokenObtainPairView)
    ```

- **Register**: `POST`
    ```
    /register/ (RegisterView)
    ```

### Example Request Headers

For authenticated requests, include the access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

## Consumers File Location

For reference and inquiries, the `TaskConsumer` class is located in:
```
api/consumers.py
```