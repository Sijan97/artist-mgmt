"""
User Profile Views.
"""

import uuid

from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.validations import date_validation


class ProfilesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    operation_id="get_user_profiles",
    responses={
        (200, "application/json"): {
            "example": {
                "user_profiles": [
                    {
                        "id": 1,
                        "email": "profile1@example.com",
                        "full_name": "Profile 1",
                        "date_of_birth": "1990-02-13",
                        "gender": "male",
                        "address": "Address 1",
                        "phone": "987654321",
                    },
                    {
                        "id": 2,
                        "email": "profile2@example.com",
                        "full_name": "Profile 2",
                        "date_of_birth": "1990-02-13",
                        "gender": "female",
                        "address": "Address 2",
                        "phone": "987654321",
                    },
                ]
            }
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_profiles(request: Request):
    """Get all user profiles."""

    paginator = ProfilesPagination()

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute(
                "SELECT p.id, u.email, (first_name || ' ' || last_name) as full_name, DATE(date_of_birth) as date_of_birth, gender, address, phone FROM core_userprofile p INNER JOIN core_user u ON p.user_id = u.id;"
            )
            columns = [col[0] for col in c.description]
            data = c.fetchall()

        result = [dict(zip(columns, row)) for row in data]

        page = paginator.paginate_queryset(result, request)

        return paginator.get_paginated_response(page)

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    operation_id="get_user_profile",
    responses={
        (200, "application/json"): {
            "example": {
                "user_profile": [
                    {
                        "id": 1,
                        "email": "profile1@example.com",
                        "full_name": "Profile 1",
                        "date_of_birth": "1990-02-13",
                        "gender": "male",
                        "address": "Address 1",
                        "phone": "987654321",
                    }
                ]
            }
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_profile(request: Request, id: str):
    """Get profile with id."""

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute(
                "SELECT p.id, u.email, first_name, last_name, DATE(date_of_birth) as date_of_birth, gender, address, phone FROM core_userprofile p INNER JOIN core_user u ON p.user_id = u.id WHERE p.id = %s;",
                [id],
            )
            columns = [col[0] for col in c.description]
            data = c.fetchall()

        result = [dict(zip(columns, row)) for row in data]

        return Response(result[0])

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    request={
        "application/json": {
            "example": {
                "user_email": "user@example.com",
                "first_name": "User",
                "last_name": "Profile",
                "phone": "987654321",
                "date_of_birth": "1995-02-13",
                "gender": "male",
                "address": "Texas, USA",
            }
        }
    },
    responses={
        (201, "application/json"): {"example": {"message": "Profile created successfully"}},
        (400, "application/json"): {"example": {"message": "Invalid JSON in request body."}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_profile(request: Request):
    """Create new user profile."""

    if request.method == "POST":
        try:
            data = request.data
            id = str(uuid.uuid4())
            user_email = data.get("user_email")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            phone = data.get("phone")
            date_of_birth = data.get("date_of_birth")
            gender = data.get("gender")
            address = data.get("address")
            created = timezone.now()
            modified = timezone.now()

            with connection.cursor() as c:
                c.execute("SELECT id FROM core_user WHERE email = %s;", [user_email])
                user = c.fetchone()

                if user:
                    if not date_validation(date_of_birth):
                        return Response({"message": "Date of birth must not be greater than present date."})

                    c.execute(
                        "INSERT INTO core_userprofile(id, user_id, first_name, last_name, phone, date_of_birth, gender, address, created, modified) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, user_id, first_name, last_name;",
                        [
                            id,
                            str(user[0]),
                            first_name,
                            last_name,
                            phone,
                            date_of_birth,
                            gender,
                            address,
                            created,
                            modified,
                        ],
                    )

                    created_profile = c.fetchone()
                else:
                    return Response({"message": f"User with email '{user_email}' not found."})

                if created_profile:
                    id, user_id, first_name, last_name = created_profile

                    return Response(
                        {
                            "message": "Profile created successfully",
                            "profile": {
                                "id": id,
                                "user_id": user_id,
                                "first_name": first_name,
                                "last_name": last_name,
                            },
                        },
                        status=status.HTTP_201_CREATED,
                    )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    request={
        "application/json": {
            "example": {
                "first_name": "User",
                "last_name": "Profile",
                "phone": "987654321",
                "date_of_birth": "1995-02-13",
                "gender": "male",
                "address": "Texas, USA",
            }
        }
    },
    responses={
        (200, "application/json"): {"example": {"message": "Profile updated successfully"}},
        (400, "application/json"): {"example": {"message": "Invalid JSON in request body."}},
    },
)
@api_view(["PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request: Request, id: str):
    """Update user profile."""

    if request.method == "PUT" or request.method == "PATCH":
        data = request.data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        phone = data.get("phone")
        date_of_birth = data.get("date_of_birth")
        gender = data.get("gender")
        address = data.get("address")
        modified = timezone.now()

        try:
            with connection.cursor() as c:
                if date_of_birth and not date_validation(date_of_birth):
                    return Response({"message": "Date of birth must not be greater than present date."})

                # Get stored data
                c.execute(
                    "SELECT first_name, last_name, phone, date_of_birth, gender, address FROM core_userprofile WHERE id = %s;",
                    [id],
                )

                user_data = c.fetchone()

                if user_data:
                    (
                        stored_first_name,
                        stored_last_name,
                        stored_phone,
                        stored_date_of_birth,
                        stored_gender,
                        stored_address,
                    ) = user_data

                    new_first_name = first_name if first_name else stored_first_name
                    new_last_name = last_name if last_name else stored_last_name
                    new_phone = phone if phone else stored_phone
                    new_date_of_birth = date_of_birth if date_of_birth else stored_date_of_birth
                    new_gender = gender if gender else stored_gender
                    new_address = address if address else stored_address

                c.execute(
                    "UPDATE core_userprofile SET first_name = %s, last_name = %s, phone = %s, date_of_birth = %s, gender = %s, address = %s, modified = %s WHERE id = %s RETURNING id, first_name, last_name, phone, date_of_birth, gender, address, modified;",
                    [
                        new_first_name,
                        new_last_name,
                        new_phone,
                        new_date_of_birth,
                        new_gender,
                        new_address,
                        modified,
                        id,
                    ],
                )
                profile_data = c.fetchone()

                if profile_data:
                    (
                        id,
                        first_name,
                        last_name,
                        phone,
                        date_of_birth,
                        gender,
                        address,
                        modified,
                    ) = profile_data

                    return Response(
                        {
                            "message": "Profile updated successfully.",
                            "profile": {
                                "id": id,
                                "first_name": first_name,
                                "last_name": last_name,
                                "phone": phone,
                                "date_of_birth": date_of_birth,
                                "gender": gender,
                                "address": address,
                                "modified": modified,
                            },
                        },
                        status=status.HTTP_200_OK,
                    )

                return Response({"message": "Failed to update profile."})
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response({"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
