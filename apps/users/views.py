"""
CRUD Operations For User.
"""

import json
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import connection
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from knox.auth import AuthToken

from apps.core.models import User
from apps.core.schema import KnoxTokenScheme  # noqa


@extend_schema(
    responses={
        (200, "application/json"): {
            "example": [
                {"id": 1, "email": "user1@example.com"},
                {"id": 2, "email": "user2@example.com"},
            ]
        }
    },
)
@api_view(["GET"])
def get_users(request):
    """Get all users."""
    if request.method == "GET":
        with connection.cursor() as c:
            c.execute("SELECT id, email FROM core_user;")
            columns = [col[0] for col in c.description]
            data = c.fetchall()

        result = [dict(zip(columns, row)) for row in data]

        return Response({"users": result})


@extend_schema(
    parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)],
    responses={
        (200, "application/json"): {
            "example": {"user": [{"id": 1, "email": "user1@example.com"}]},
        }
    },
)
@api_view(["GET"])
def get_user(request, id):
    """Get a specific user."""
    if request.method == "GET":
        with connection.cursor() as c:
            c.execute("SELECT id, email FROM core_user WHERE id = %s", [id])
            columns = [col[0] for col in c.description]
            data = c.fetchall()

        result = [dict(zip(columns, row)) for row in data]

        return Response({"user": result})


@extend_schema(
    request={
        "application/json": {
            "example": {
                "email": "user@example.com",
                "old_password": "oldpassw",
                "new_password": "newpass",
            }
        }
    },
    responses={
        (200, "application/json"): {"example": "Password changed successfully"},
        (400, "application/json"): {
            "example": "Invalid credentials or invalid JSON in request body"
        },
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def change_password(request):
    """Change user password."""
    if request.method == "POST":
        try:
            data = request.data
            email = data.get("email")
            old_password = data.get("old_password")
            new_password = make_password(data.get("new_password"))

            with connection.cursor() as c:
                c.execute(
                    "SELECT id, password FROM core_user WHERE email = %s", [email]
                )
                user_data = c.fetchone()

            if user_data:
                id, stored_password = user_data

                if check_password(old_password, stored_password):
                    # If the old password is correct, update the password to the new password
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE core_user SET password = %s WHERE id = %s",
                            [new_password, id],
                        )

                    return Response({"message": "Password changed successfully"})

            return Response(
                {"message": "Invalid Email or Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except json.JSONDecodeError:
            return Response(
                {"message": "Invalid JSON in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    request={
        "application/json": {
            "example": {
                "email": "user@example.com",
                "password": "password",
                "confirm_password": "password",
            }
        }
    },
    responses={
        (200, "application/json"): {
            "example": {
                "message": "User Created",
                "id": "1Sw1sFa-1298as-sf124124-12341k",
                "email": "user@example.com",
                "token": "120975412sad12d811",
            }
        },
        (400, "application/json"): {"example": {"message": "Falied to create user"}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def user_register(request):
    """Register new user."""

    if request.method == "POST":
        try:
            data = request.data
            id = str(uuid.uuid4())
            email = data.get("email")
            password = data.get("password")
            confirm_password = data.get("confirm_password")
            hashed_password = make_password(password)
            date_joined = timezone.now()

            with connection.cursor() as c:
                c.execute("SELECT id FROM core_user WHERE email = %s", [email])
                existing_user = c.fetchone()

                if existing_user:
                    return Response(
                        {"message": "User already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if password == confirm_password:
                    c.execute(
                        "INSERT INTO core_user (id, email, password, is_superuser, is_staff, is_active, date_joined) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, email",
                        [id, email, hashed_password, False, False, True, date_joined],
                    )

                    created_user = c.fetchone()

                if created_user:
                    id, email = created_user

                    user = User.objects.get(id=id)
                    knox_token = AuthToken.objects.create(user)[1]

                    return Response(
                        {
                            "message": "User Created",
                            "id": id,
                            "email": email,
                            "token": knox_token,
                        }
                    )

                return Response({"message": "Password did not match"})
        except:
            return Response({"message": "Failed to create user"})


@extend_schema(
    request={
        "application/json": {
            "example": {"email": "user@example.com", "password": "password"}
        }
    },
    responses={
        (200, "application/json"): {
            "example": {
                "message": "Login Successful",
                "id": "1Sw1sFa-1298as-sf124124-12341k",
                "email": "user@example.com",
                "token": "194071249126h81d18hd912",
            }
        },
        (401, "application/json"): {
            "example": {"message": "Invalid Credentials", "status": "401"}
        },
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    """User login with email and password."""
    if request.method == "POST":
        try:
            data = request.data
            email = data.get("email")
            password = data.get("password")
            with connection.cursor() as c:
                c.execute(
                    "SELECT id, password FROM core_user WHERE email = %s", [email]
                )
                user_data = c.fetchone()

            if user_data:
                id, stored_password = user_data

                if check_password(password, stored_password):
                    user = User.objects.get(id=id)
                    knox_token = AuthToken.objects.create(user)[1]

                    return Response(
                        {
                            "message": "Login Successful",
                            "id": id,
                            "email": email,
                            "token": knox_token,
                        }
                    )

                return Response(
                    {"message": "Invalid Credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except:
            return Response({"message": "Login Failed"})

    return Response(
        {"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
