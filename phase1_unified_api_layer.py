"""
Unified API Layer for IDEA System
===================================

This module provides a unified API layer that standardizes all API endpoints
across the IDEA system. It ensures consistent request/response formats,
authentication, and error handling.

Author: Manus AI
Date: 2025-10-20
"""

from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Tuple

# Configuration
API_VERSION = "v1"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
TOKEN_EXPIRY = 24  # hours


class UnifiedAPIResponse:
    """
    Standardized response format for all API endpoints.
    Ensures consistent response structure across the system.
    """

    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[Dict, int]:
        """
        Return a successful API response.

        Args:
            data: The response data payload
            message: Success message
            status_code: HTTP status code

        Returns:
            Tuple of (response_dict, status_code)
        """
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }, status_code

    @staticmethod
    def error(message: str, error_code: str = "ERROR", status_code: int = 400, details: Dict = None) -> Tuple[Dict, int]:
        """
        Return an error API response.

        Args:
            message: Error message
            error_code: Unique error code
            status_code: HTTP status code
            details: Additional error details

        Returns:
            Tuple of (response_dict, status_code)
        """
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }, status_code

    @staticmethod
    def paginated(data: list, page: int, page_size: int, total: int, message: str = "Success") -> Tuple[Dict, int]:
        """
        Return a paginated API response.

        Args:
            data: List of items
            page: Current page number
            page_size: Items per page
            total: Total number of items
            message: Success message

        Returns:
            Tuple of (response_dict, status_code)
        """
        return {
            "status": "success",
            "message": message,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            },
            "timestamp": datetime.utcnow().isoformat()
        }, 200


class TokenManager:
    """
    Manages JWT token generation and validation for API authentication.
    """

    @staticmethod
    def generate_token(user_id: str, user_type: str = "user") -> str:
        """
        Generate a JWT token for a user.

        Args:
            user_id: User identifier
            user_type: Type of user (user, admin, team_member)

        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "user_type": user_type,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")


def require_auth(f: Callable) -> Callable:
    """
    Decorator to require authentication for API endpoints.
    Validates JWT token from Authorization header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return UnifiedAPIResponse.error(
                "Missing authorization header",
                "AUTH_MISSING",
                401
            )

        try:
            token = auth_header.split(" ")[1]
            payload = TokenManager.verify_token(token)
            request.user = payload
        except (IndexError, ValueError) as e:
            return UnifiedAPIResponse.error(
                str(e),
                "AUTH_INVALID",
                401
            )

        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific user roles for API endpoints.
    Must be used after require_auth decorator.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, "user"):
                return UnifiedAPIResponse.error(
                    "User not authenticated",
                    "AUTH_REQUIRED",
                    401
                )

            user_type = request.user.get("user_type")
            if user_type not in allowed_roles:
                return UnifiedAPIResponse.error(
                    "Insufficient permissions",
                    "FORBIDDEN",
                    403
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


class UnifiedAPIServer:
    """
    Main unified API server that aggregates all system endpoints.
    """

    def __init__(self, app: Flask = None):
        """
        Initialize the unified API server.

        Args:
            app: Flask application instance
        """
        self.app = app or Flask(__name__)
        CORS(self.app)
        self.setup_routes()

    def setup_routes(self):
        """Setup all API routes and blueprints."""
        # Health check endpoint
        @self.app.route(f"/api/{API_VERSION}/health", methods=["GET"])
        def health_check():
            return UnifiedAPIResponse.success({
                "status": "healthy",
                "version": API_VERSION,
                "timestamp": datetime.utcnow().isoformat()
            })

        # Authentication endpoints
        @self.app.route(f"/api/{API_VERSION}/auth/login", methods=["POST"])
        def login():
            """
            User login endpoint.
            Expects JSON body with 'email' and 'password'.
            """
            data = request.get_json()

            if not data or not data.get("email") or not data.get("password"):
                return UnifiedAPIResponse.error(
                    "Email and password are required",
                    "INVALID_CREDENTIALS",
                    400
                )

            # TODO: Validate credentials against database
            # This is a placeholder - implement actual authentication
            user_id = "user_123"  # Replace with actual user lookup
            token = TokenManager.generate_token(user_id, "user")

            return UnifiedAPIResponse.success({
                "token": token,
                "user_id": user_id,
                "expires_in": TOKEN_EXPIRY * 3600
            }, "Login successful", 200)

        @self.app.route(f"/api/{API_VERSION}/auth/logout", methods=["POST"])
        @require_auth
        def logout():
            """User logout endpoint."""
            return UnifiedAPIResponse.success(message="Logout successful")

        # Projects endpoints
        @self.app.route(f"/api/{API_VERSION}/projects", methods=["GET"])
        @require_auth
        def get_projects():
            """
            Get all projects for the authenticated user.
            Supports pagination and filtering.
            """
            page = request.args.get("page", 1, type=int)
            page_size = request.args.get("page_size", 10, type=int)
            status = request.args.get("status", None)

            # TODO: Fetch projects from database based on user_id
            # This is a placeholder
            projects = []
            total = 0

            return UnifiedAPIResponse.paginated(
                projects,
                page,
                page_size,
                total,
                "Projects retrieved successfully"
            )

        @self.app.route(f"/api/{API_VERSION}/projects/<project_id>", methods=["GET"])
        @require_auth
        def get_project(project_id):
            """Get a specific project by ID."""
            # TODO: Fetch project from database
            project = {}

            if not project:
                return UnifiedAPIResponse.error(
                    "Project not found",
                    "NOT_FOUND",
                    404
                )

            return UnifiedAPIResponse.success(project, "Project retrieved successfully")

        @self.app.route(f"/api/{API_VERSION}/projects", methods=["POST"])
        @require_auth
        def create_project():
            """Create a new project."""
            data = request.get_json()

            if not data or not data.get("name"):
                return UnifiedAPIResponse.error(
                    "Project name is required",
                    "INVALID_DATA",
                    400
                )

            # TODO: Create project in database
            new_project = {
                "id": "project_123",
                "name": data.get("name"),
                "created_at": datetime.utcnow().isoformat()
            }

            return UnifiedAPIResponse.success(
                new_project,
                "Project created successfully",
                201
            )

        @self.app.route(f"/api/{API_VERSION}/projects/<project_id>", methods=["PUT"])
        @require_auth
        def update_project(project_id):
            """Update an existing project."""
            data = request.get_json()

            # TODO: Update project in database
            updated_project = {
                "id": project_id,
                "updated_at": datetime.utcnow().isoformat(),
                **data
            }

            return UnifiedAPIResponse.success(
                updated_project,
                "Project updated successfully"
            )

        @self.app.route(f"/api/{API_VERSION}/projects/<project_id>", methods=["DELETE"])
        @require_auth
        def delete_project(project_id):
            """Delete a project."""
            # TODO: Delete project from database
            return UnifiedAPIResponse.success(
                message="Project deleted successfully"
            )

        # Tasks endpoints
        @self.app.route(f"/api/{API_VERSION}/tasks", methods=["GET"])
        @require_auth
        def get_tasks():
            """Get all tasks for the authenticated user."""
            project_id = request.args.get("project_id")
            status = request.args.get("status")
            page = request.args.get("page", 1, type=int)
            page_size = request.args.get("page_size", 10, type=int)

            # TODO: Fetch tasks from database
            tasks = []
            total = 0

            return UnifiedAPIResponse.paginated(
                tasks,
                page,
                page_size,
                total,
                "Tasks retrieved successfully"
            )

        @self.app.route(f"/api/{API_VERSION}/tasks", methods=["POST"])
        @require_auth
        def create_task():
            """Create a new task."""
            data = request.get_json()

            if not data or not data.get("title"):
                return UnifiedAPIResponse.error(
                    "Task title is required",
                    "INVALID_DATA",
                    400
                )

            # TODO: Create task in database
            new_task = {
                "id": "task_123",
                "title": data.get("title"),
                "created_at": datetime.utcnow().isoformat()
            }

            return UnifiedAPIResponse.success(
                new_task,
                "Task created successfully",
                201
            )

        # Error handler for 404
        @self.app.errorhandler(404)
        def not_found(error):
            return UnifiedAPIResponse.error(
                "Endpoint not found",
                "NOT_FOUND",
                404
            )

        # Error handler for 500
        @self.app.errorhandler(500)
        def internal_error(error):
            return UnifiedAPIResponse.error(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """
        Run the unified API server.

        Args:
            host: Server host address
            port: Server port
            debug: Enable debug mode
        """
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    app = Flask(__name__)
    api_server = UnifiedAPIServer(app)
    api_server.run(debug=True)

