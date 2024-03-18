"""
CRUD Operations For User.
"""

import json
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.db import connection, transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from knox.auth import AuthToken
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.models import User
from apps.core.schema import KnoxTokenScheme  # noqa
from apps.core.validations import email_validation, password_validation
from apps.profiles.signals import create_profile_handler


@extend_schema(
    operation_id="get_users",
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
@permission_classes([permissions.IsAdminUser])
def get_users(request: Request):
    """Get all users."""

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute("SELECT id, email FROM core_user;")
            columns = [col[0] for col in c.description]
            data = c.fetchall()

        result = [dict(zip(columns, row)) for row in data]

        return Response({"users": result})

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    operation_id="get_user",
    responses={
        (200, "application/json"): {
            "example": {"user": [{"id": 1, "email": "user1@example.com"}]},
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_user(request: Request, id: str):
    """Get a specific user."""

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute("SELECT id, email FROM core_user WHERE id = %s;", [id])
            columns = [col[0] for col in c.description]
            data = c.fetchall()

        result = [dict(zip(columns, row)) for row in data]

        return Response({"user": result})

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    responses={
        (200, "application/json"): {
            "example": {"user": {"id": 1, "email": "user1@example.com"}},
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request: Request):
    """Get authenticated user."""

    if request.method == "GET":
        authenticated_user = request.user

        return Response({"user": {"id": authenticated_user.id, "email": authenticated_user.email}})

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    request={
        "application/json": {
            "example": {
                "email": "user@example.com",
                "old_password": "oldpassw",
                "new_password": "newpass",
                "confirm_password": "newpass",
            }
        }
    },
    responses={
        (200, "application/json"): {"example": "Password changed successfully"},
        (400, "application/json"): {"example": "Invalid credentials or invalid JSON in request body"},
    },
)
@api_view(["PATCH"])
@permission_classes([permissions.AllowAny])
def change_password(request: Request):
    """Change user password."""

    if request.method == "PATCH":
        try:
            data = request.data
            email = data.get("email")
            old_password = data.get("old_password")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")
            hashed_password = make_password(new_password)

            with connection.cursor() as c:
                # Validate email
                if not email_validation(email):
                    return Response({"message": "Invalid email."})

                c.execute("SELECT id, password FROM core_user WHERE email = %s;", [email])
                user_data = c.fetchone()

            if user_data:
                id, stored_password = user_data

                # If the old password is correct, update the password to the new password
                if check_password(old_password, stored_password):
                    # Check confirm password
                    if new_password == confirm_password:
                        # Validate password
                        if not password_validation(new_password):
                            return Response({"message": "Please enter a strong password with at least 8 characters."})
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE core_user SET password = %s WHERE id = %s;",
                                [hashed_password, id],
                            )

                        return Response({"message": "Password changed successfully"})

                    return Response({"message": "New password and confirm password must match."})

                return Response({"message": "Incorrect old password."})

            return Response(
                {"message": "Invalid Email or Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except json.JSONDecodeError:
            return Response(
                {"message": "Invalid JSON in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
        (201, "application/json"): {
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
def user_register(request: Request):
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
            created = timezone.now()
            modified = timezone.now()

            with connection.cursor() as c:
                # Validate email
                if not email_validation(email):
                    return Response(
                        {"message": "Invalid email."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                c.execute("SELECT id FROM core_user WHERE email = %s;", [email])
                existing_user = c.fetchone()

                if existing_user:
                    return Response(
                        {"message": "User already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not password_validation(password):
                    return Response(
                        {"message": "Please enter a strong password with at least 8 characters."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if password == confirm_password:
                    c.execute(
                        "INSERT INTO core_user (id, email, password, is_superuser, is_staff, is_active, date_joined, created, modified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, email;",
                        [
                            id,
                            email,
                            hashed_password,
                            False,
                            False,
                            True,
                            date_joined,
                            created,
                            modified,
                        ],
                    )

                    created_user = c.fetchone()
                else:
                    return Response(
                        {"message": "Password did not match"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if created_user:
                    id, email = created_user

                    user = User.objects.get(id=id)

                    # Send signal to create user profile
                    create_profile_handler(sender=User, instance=user, created=True)

                    # Generate token
                    knox_token = AuthToken.objects.create(user)[1]

                    return Response(
                        {
                            "message": "User Created",
                            "id": id,
                            "email": email,
                            "token": knox_token,
                        },
                        status=status.HTTP_201_CREATED,
                    )
        except json.JSONDecodeError:
            return Response(
                {"message": "Failed to create user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    request={"application/json": {"example": {"email": "user@example.com", "password": "password"}}},
    responses={
        (200, "application/json"): {
            "example": {
                "message": "Login Successful",
                "id": "1Sw1sFa-1298as-sf124124-12341k",
                "email": "user@example.com",
                "token": "194071249126h81d18hd912",
            }
        },
        (401, "application/json"): {"example": {"message": "Invalid Credentials", "status": "401"}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request: Request):
    """User login with email and password."""

    if request.method == "POST":
        try:
            data = request.data
            email = data.get("email")
            password = data.get("password")
            with connection.cursor() as c:
                # Validate email
                if not email_validation(email):
                    return Response({"message": "Invalid email."})

                c.execute("SELECT id, password FROM core_user WHERE email = %s;", [email])
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
                        },
                        status=status.HTTP_200_OK,
                    )

                return Response(
                    {"message": "Invalid Credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return Response(
                {"message": "User with given credentials not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    request=None,
    responses={
        (200, "application/json"): {"example": {"message": "Logout Successful"}},
        (405, "application/json"): {"example": {"message": "Invalid request method"}},
    },
)
@api_view(["POST"])
@login_required
def logout(request: Request):
    """Logout user."""

    if request.method == "POST":
        user = request.user
        AuthToken.objects.filter(user=user).delete()

        return Response({"message": "Logout Successful"})

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    request=None,
    responses={
        (200, "application/json"): {"example": {"message": "User deleted successfully"}},
        (405, "application/json"): {"example": {"message": "Invalid request method"}},
    },
)
@api_view(["DELETE"])
@permission_classes([permissions.IsAdminUser])
def delete_user(request: Request, id: str):
    """Delete inactive user."""

    if request.method == "DELETE":
        with transaction.atomic(using=connection.alias), connection.cursor() as c:
            try:
                # Delete all tokens for the user.
                c.execute("DELETE FROM knox_authtoken WHERE user_id = %s;", [id])

                # Delete user profile
                c.execute("DELETE FROM core_userprofile WHERE user_id = %s;", [id])

                # Delete user from table.
                c.execute(
                    "DELETE FROM core_user WHERE id = %s;",
                    [id],
                )

                return Response(
                    {
                        "message": "User deleted successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
