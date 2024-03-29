"""
Artist Profile Views.
"""

import uuid

from django.db import connection, transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.validations import date_validation, integer_validation


class ArtistsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    operation_id="get_artists",
    responses={
        (200, "application/json"): {
            "example": {
                "count": 2,
                "next": "http://localhost:8000/artists/?page=2",
                "previous": None,
                "results": [
                    {
                        "id": "21321-dsa123-1d1d13-54ts34",
                        "name": "Artist",
                        "first_release_year": 1987,
                        "no_of_albums_released": 25,
                        "date_of_birth": "1965-03-12",
                        "gender": "male",
                        "address": "New York, USA",
                    },
                    {
                        "id": "21321-dsa123-1d1d13-54ts34",
                        "name": "Another Artist",
                        "first_release_year": 1990,
                        "no_of_albums_released": 15,
                        "date_of_birth": "1970-11-22",
                        "gender": "female",
                        "address": "London, UK",
                    },
                ],
            }
        },
        (405, "application/json"): {"example": "Invalid request method."},
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_artists(request: Request):
    """Get all artists."""
    paginator = ArtistsPagination()

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute(
                "SELECT id, name, first_release_year, no_of_albums_released, DATE(date_of_birth) as date_of_birth, gender, address FROM core_artistprofile;"
            )

            columns = [col[0] for col in c.description]
            artist_data = c.fetchall()

        result = [dict(zip(columns, row)) for row in artist_data]

        page = paginator.paginate_queryset(result, request)

        return paginator.get_paginated_response(page)

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    operation_id="get_artist",
    responses={
        (200, "application/json"): {
            "example": {
                "artist": [
                    {
                        "id": "21321-dsa123-1d1d13-54ts34",
                        "name": "Artist",
                        "first_release_year": 1987,
                        "no_of_albums_released": 25,
                        "date_of_birth": "1965-03-12",
                        "gender": "male",
                        "address": "New York, USA",
                    },
                ]
            }
        },
        (405, "application/json"): {"example": {"message": "Invalid request method."}},
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_artist(request: Request, id: str):
    """Get artist with id."""

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute(
                "SELECT id, name, first_release_year, no_of_albums_released, DATE(date_of_birth) as date_of_birth, gender, address FROM core_artistprofile WHERE id = %s;",
                [id],
            )

            columns = [col[0] for col in c.description]
            artist_data = c.fetchall()

        result = [dict(zip(columns, row)) for row in artist_data]

        return Response(result[0])

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    request={
        "application/json": {
            "example": {
                "name": "Artist",
                "first_release_year": 1987,
                "no_of_albums_released": 25,
                "date_of_birth": "1965-03-12",
                "gender": "male",
                "address": "New York, USA",
            }
        }
    },
    responses={
        (201, "application/json"): {
            "example": {
                "message": "Artist created successfully",
                "artist": {
                    "id": "21321-dsa123-1d1d13-54ts34",
                    "name": "Artist",
                    "first_release_year": 1987,
                    "no_of_albums_released": 25,
                    "date_of_birth": "1965-03-12",
                    "gender": "male",
                    "address": "New York, USA",
                },
            }
        },
        (400, "application/json"): {"example": {"message": "Failed to create artist."}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_artist(request: Request):
    """Add new artist."""
    if request.method == "POST":
        try:
            data = request.data
            id = str(uuid.uuid4())
            name = data.get("name")
            first_release_year = int(data.get("first_release_year"))
            no_of_albums_released = int(data.get("no_of_albums_released"))
            date_of_birth = data.get("date_of_birth")
            gender = data.get("gender")
            address = data.get("address")
            created = timezone.now()
            modified = timezone.now()

            with connection.cursor() as c:
                # Validate integers
                if not integer_validation(first_release_year):
                    return Response({"message": "Please enter a valid release year"})

                if not integer_validation(no_of_albums_released):
                    return Response({"message": "Please enter a valid number of albums released."})

                # Validate date of birth
                if not date_validation(date_of_birth):
                    return Response({"message": "Date of birth must not be greater than present date."})

                c.execute(
                    "INSERT INTO core_artistprofile(id, name, first_release_year, no_of_albums_released, date_of_birth, gender, address, created, modified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, name, first_release_year, no_of_albums_released, date_of_birth, gender, address;",
                    [
                        id,
                        name,
                        first_release_year,
                        no_of_albums_released,
                        date_of_birth,
                        gender,
                        address,
                        created,
                        modified,
                    ],
                )

                created_artist = c.fetchone()

            if created_artist:
                (
                    id,
                    name,
                    first_release_year,
                    no_of_albums_released,
                    date_of_birth,
                    gender,
                    address,
                ) = created_artist

                return Response(
                    {
                        "message": "Artist created successfully",
                        "artist": {
                            "id": id,
                            "name": name,
                            "first_release_year": first_release_year,
                            "no_of_albums_released": no_of_albums_released,
                            "date_of_birth": date_of_birth,
                            "gender": gender,
                            "address": address,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response({"message": "Failed to create artist."})
        except Exception as e:
            return Response({"messsage": str(e)})

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    request={
        "application/json": {
            "example": {
                "name": "Artist",
                "first_release_year": 1987,
                "no_of_albums_released": 25,
                "date_of_birth": "1965-03-12",
                "gender": "male",
                "address": "New York, USA",
            }
        }
    },
    responses={
        (200, "application/json"): {
            "example": {
                "message": "Artist updated successfully",
                "artist": {
                    "id": "21321-dsa123-1d1d13-54ts34",
                    "name": "Artist",
                    "first_release_year": 1987,
                    "no_of_albums_released": 25,
                    "date_of_birth": "1965-03-12",
                    "gender": "male",
                    "address": "New York, USA",
                },
            }
        },
        (400, "application/json"): {"example": {"message": "Failed to update artist."}},
    },
)
@api_view(["PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_artist(request: Request, id: str):
    """Update existing artist."""

    if request.method == "PUT" or request.method == "PATCH":
        try:
            data = request.data
            name = data.get("name")
            first_release_year = data.get("first_release_year")
            no_of_albums_released = data.get("no_of_albums_released")
            date_of_birth = data.get("date_of_birth")
            gender = data.get("gender")
            address = data.get("address")
            modified = timezone.now()

            with connection.cursor() as c:
                # Validate integers
                if first_release_year and not integer_validation(first_release_year):
                    return Response({"message": "Please enter a valid release year"})

                if no_of_albums_released and not integer_validation(no_of_albums_released):
                    return Response({"message": "Please enter a valid number of albums released."})

                # Validate date of birth
                if date_of_birth and not date_validation(date_of_birth):
                    return Response({"message": "Date of birth must not be greater than present date."})

                # Get stored data
                c.execute(
                    "SELECT name, first_release_year, no_of_albums_released, date_of_birth, gender, address FROM core_artistprofile WHERE id = %s;",
                    [id],
                )
                artist_data = c.fetchone()

                if artist_data:
                    (
                        stored_name,
                        stored_first_release_year,
                        stored_no_of_albums_released,
                        stored_date_of_birth,
                        stored_gender,
                        stored_address,
                    ) = artist_data

                    new_name = name if name else stored_name
                    new_first_release_year = first_release_year if first_release_year else stored_first_release_year
                    new_no_of_albums_released = (
                        no_of_albums_released if no_of_albums_released else stored_no_of_albums_released
                    )
                    new_date_of_birth = date_of_birth if date_of_birth else stored_date_of_birth
                    new_gender = gender if gender else stored_gender
                    new_address = address if address else stored_address

                c.execute(
                    "UPDATE core_artistprofile SET name = %s, first_release_year = %s, no_of_albums_released = %s, date_of_birth = %s, gender = %s, address = %s, modified = %s WHERE id = %s RETURNING id, name, first_release_year, no_of_albums_released, date_of_birth, gender, address;",
                    [
                        new_name,
                        new_first_release_year,
                        new_no_of_albums_released,
                        new_date_of_birth,
                        new_gender,
                        new_address,
                        modified,
                        id,
                    ],
                )

                updated_artist = c.fetchone()

            if updated_artist:
                (
                    id,
                    name,
                    first_release_year,
                    no_of_albums_released,
                    date_of_birth,
                    gender,
                    address,
                ) = updated_artist

                return Response(
                    {
                        "message": "Artist updated successfully",
                        "artist": {
                            "id": id,
                            "name": name,
                            "first_release_year": first_release_year,
                            "no_of_albums_released": no_of_albums_released,
                            "date_of_birth": date_of_birth,
                            "gender": gender,
                            "address": address,
                        },
                    }
                )

            return Response({"message": "Failed to update artist"})
        except Exception as e:
            return Response({"message": str(e)})

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    request=None,
    responses={
        (200, "application/json"): {"example": {"message": "Artist deleted successfully"}},
        (405, "application/json"): {"example": {"message": "Invalid request method"}},
    },
)
@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_artist(request: Request, id: str):
    """Delete existing artist."""

    if request.method == "DELETE":
        with transaction.atomic(using=connection.alias), connection.cursor() as c:
            try:
                # Delete artist record from intermediatary table.
                c.execute(
                    "DELETE FROM core_music_artists WHERE artistprofile_id = %s;",
                    [id],
                )

                # Delete artist from table.
                c.execute(
                    "DELETE FROM core_artistprofile WHERE id = %s;",
                    [id],
                )

                return Response(
                    {
                        "message": "Artist deleted successfully.",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"message": str(e)})

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )
