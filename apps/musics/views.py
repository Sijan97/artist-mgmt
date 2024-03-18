"""
API Views For Music App.
"""

import uuid

from django.db import connection, transaction
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.validations import date_validation


class MusicsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    operation_id="get_musics",
    responses={
        (200, "application/json"): {
            "example": {
                "musics": [
                    {
                        "id": "21321-dsa123-1d1d13-54ts34",
                        "title": "Music",
                        "release_date": 1987,
                        "album_name": "Album 1",
                        "genre": "rnb",
                        "artists": [
                            "Artist 1",
                            "Artist 2",
                        ],
                    },
                    {
                        "id": "21321-dsa123-1d1d13-54ts34",
                        "title": "Another Music",
                        "release_date": 1990,
                        "album_name": "Album 2",
                        "genre": "country",
                        "artists": [
                            "Artist 1",
                            "Artist 2",
                        ],
                    },
                ]
            }
        },
        (405, "application/json"): {"example": {"message": "Invalid request method."}},
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_musics(request: Request):
    """Get all musics"""
    paginator = MusicsPagination()

    if request.method == "GET":
        with connection.cursor() as c:
            # c.execute(
            #     "SELECT m.id, title, release_date, album_name, genre, a.name FROM core_music m INNER JOIN core_music_artists ma ON m.id = ma.music_id INNER JOIN core_artistprofile a ON ma.artistprofile_id = a.id;"
            # )

            c.execute("SELECT id, title, release_date, album_name, genre FROM core_music;")
            music_data = c.fetchall()

            music_list = []
            for music in music_data:
                music_info = {
                    "id": music[0],
                    "title": music[1],
                    "release_date": music[2],
                    "album_name": music[3],
                    "genre": music[4],
                }

                c.execute(
                    "SELECT artistprofile_id FROM core_music_artists WHERE music_id = %s",
                    [music_info["id"]],
                )
                artist_ids = c.fetchall()

                artist_list = []
                for artist_id in artist_ids:
                    c.execute(
                        "SELECT id, name FROM core_artistprofile WHERE id = %s",
                        [artist_id[0]],
                    )
                    artist_data = c.fetchone()

                    if artist_data:
                        artist_name = artist_data[1]
                        artist_list.append(artist_name)

                music_info["artists"] = artist_list
                music_list.append(music_info)

        page = paginator.paginate_queryset(music_list, request)

        return paginator.get_paginated_response(page)

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    operation_id="get_music",
    responses={
        (200, "application/json"): {
            "example": {
                "music": {
                    "id": "21321-dsa123-1d1d13-54ts34",
                    "title": "Music",
                    "release_date": 1987,
                    "album_name": "Album 1",
                    "genre": "rnb",
                    "artists": [
                        "Artist 1",
                        "Artist 2",
                    ],
                },
            }
        },
        (405, "application/json"): {"example": {"message": "Invalid request method."}},
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_music(request: Request, id: str):
    """Get music with id."""

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute(
                "SELECT id, title, release_date, album_name, genre FROM core_music WHERE id = %s;",
                [id],
            )
            music_data = c.fetchone()

            if music_data:
                music_info = {
                    "id": music_data[0],
                    "title": music_data[1],
                    "release_date": music_data[2],
                    "album_name": music_data[3],
                    "genre": music_data[4],
                }

                c.execute(
                    "SELECT artistprofile_id FROM core_music_artists WHERE music_id = %s",
                    [str(music_info["id"])],
                )
                artist_ids = c.fetchall()

                artist_list = []
                for artist_id in artist_ids:
                    c.execute(
                        "SELECT id, name FROM core_artistprofile WHERE id = %s",
                        [str(artist_id[0])],
                    )
                    artist_data = c.fetchall()

                    if artist_data:
                        artist_name = artist_data[0][1]
                        artist_list.append(artist_name)

                music_info["artists"] = artist_list

        return Response(music_info, status=status.HTTP_200_OK)

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    operation_id="get_music_by_artist",
    parameters=[
        OpenApiParameter("artist_id", OpenApiTypes.UUID, OpenApiParameter.PATH),
    ],
    responses={
        (200, "application/json"): {
            "example": {
                "musics": [
                    {
                        "id": "21321-dsa123-1d1d13-54ts34",
                        "title": "Music",
                        "release_date": 1987,
                        "album_name": "Album 1",
                        "genre": "rnb",
                    },
                    {
                        "id": "21321-dsa123-1d1d13-54ts34",
                        "title": "Another Music",
                        "release_date": 1990,
                        "album_name": "Album 2",
                        "genre": "country",
                    },
                ]
            }
        },
        (405, "application/json"): {"example": {"message": "Invalid request method."}},
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_music_by_artist(request: Request, artist_id: str):
    """Get music by artist."""

    if request.method == "GET":
        with connection.cursor() as c:
            c.execute(
                "SELECT m.id, m.title, m.release_date, m.album_name, m.genre FROM core_artistprofile a INNER JOIN core_music_artists ma ON a.id = ma.artistprofile_id INNER JOIN core_music m ON ma.music_id = m.id WHERE a.id = %s;",
                [artist_id],
            )

            columns = [col[0] for col in c.description]
            music_data = c.fetchall()

        result = [dict(zip(columns, row)) for row in music_data]

        return Response({"musics": result}, status=status.HTTP_200_OK)

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    request={
        "application/json": {
            "example": {
                "title": "Music",
                "release_date": "1998-12-15",
                "album_name": "Album",
                "genre": "rnb",
                "artist_ids": [
                    "4651dq-8q8qd4-812dq3-q4d451",
                    "46512q-8q8qf4-845aq3-q4d021",
                ],
            }
        }
    },
    responses={
        (201, "application/json"): {
            "example": {
                "message": "Music added successfully",
                "music": {
                    "id": "987asf-qf165-y5211r-974daq",
                    "title": "Music",
                    "release_date": "1998-12-15",
                    "album_name": "Album",
                    "genre": "rnb",
                    "artists": [
                        "Artist 1",
                        "Artist 2",
                    ],
                },
            }
        },
        (400, "application/json"): {"example": {"message": "Invalid JSON in request body."}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_music(request: Request):
    """Add new music."""

    if request.method == "POST":
        try:
            data = request.data
            id = uuid.uuid4()
            title = data.get("title")
            release_date = data.get("release_date")
            album_name = data.get("album_name")
            genre = data.get("genre")
            created = timezone.now()
            modified = timezone.now()
            artist_ids = data.get("artist_ids", [])

            with connection.cursor() as c:
                # Validate release date
                if not date_validation(release_date):
                    return Response({"message": "Release date must not be greater than present date."})

                c.execute(
                    "INSERT INTO core_music(id, title, release_date, album_name, genre, created, modified) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, title, release_date, album_name, genre;",
                    [
                        str(id),
                        title,
                        release_date,
                        album_name,
                        genre,
                        created,
                        modified,
                    ],
                )
                music_data = c.fetchone()

                if music_data:
                    music_details = {
                        "id": music_data[0],
                        "title": music_data[1],
                        "release_date": music_data[2],
                        "album_name": music_data[3],
                        "genre": music_data[4],
                    }
                    music_artist_id = uuid.uuid4()

                    artist_names = []
                    for artist_id in artist_ids:
                        c.execute(
                            "SELECT id, name FROM core_artistprofile WHERE id = %s;",
                            [artist_id],
                        )
                        artist_data = c.fetchone()

                        if not artist_data:
                            return Response({"message": "Artist not found."})

                        if artist_data:
                            artist_detail = {
                                "id": artist_data[0],
                                "name": artist_data[1],
                            }
                            artist_names.append(artist_detail["name"])

                            c.execute(
                                "INSERT INTO core_music_artists(id, music_id, artistprofile_id) VALUES (%s, %s, %s) RETURNING artistprofile_id;",
                                [music_artist_id, music_details["id"], artist_id],
                            )

                    music_details["artists"] = artist_names

            return Response(
                {"message": "Music added successfully.", "music": music_details},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"message": str(e)})

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    request={
        "application/json": {
            "example": {
                "title": "Music",
                "release_date": "1998-12-15",
                "album_name": "Album",
                "genre": "rnb",
                "artist_ids": [
                    "4651dq-8q8qd4-812dq3-q4d451",
                    "46512q-8q8qf4-845aq3-q4d021",
                ],
            }
        }
    },
    responses={
        (200, "application/json"): {
            "example": {
                "message": "Music updated successfully",
                "music": {
                    "id": "987asf-qf165-y5211r-974daq",
                    "title": "Updated Music",
                    "release_date": "1998-12-15",
                    "album_name": "Updated Album",
                    "genre": "rnb",
                    "artists": [
                        "Artist 1",
                        "Artist 2",
                    ],
                },
            }
        },
        (400, "application/json"): {"example": {"message": "Invalid JSON in request body."}},
    },
)
@api_view(["PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_music(request: Request, id: str):
    """Update existing music."""

    if request.method == "PUT" or request.method == "PATCH":
        data = request.data
        title = data.get("title")
        release_date = data.get("release_date")
        album_name = data.get("album_name")
        genre = data.get("genre")
        modified = timezone.now()
        artist_ids = data.get("artist_ids", [])

        with transaction.atomic(using=connection.alias), connection.cursor() as c:
            try:
                # Validate release date
                if release_date and not date_validation(release_date):
                    return Response({"message": "Release date must not be greater than present date."})

                # Get stored data
                c.execute(
                    "SELECT title, release_date, album_name, genre, core_music_artists.artistprofile_id as artists FROM core_music INNER JOIN core_music_artists ON core_music.id = core_music_artists.music_id WHERE core_music.id = %s;",
                    [str(id)],
                )

                music_data = c.fetchall()
                print(f"Music Data =============> {music_data}")

                if music_data:
                    artist_list = []
                    for music in music_data:
                        music_details = {
                            "stored_title": music[0],
                            "stored_release_date": music[1],
                            "stored_album_name": music[2],
                            "stored_genre": music[3],
                            "stored_artist_ids": music[4],
                        }

                        new_title = title if title else music_details["stored_title"]
                        new_release_date = release_date if release_date else music_details["stored_release_date"]
                        new_album_name = album_name if album_name else music_details["stored_album_name"]
                        new_genre = genre if genre else music_details["stored_genre"]
                        artist_list.append(music_details["stored_artist_ids"])
                        new_artist_ids = artist_ids if artist_ids else artist_list

                c.execute(
                    "UPDATE core_music SET title = %s, release_date = %s, album_name = %s, genre = %s, modified = %s WHERE id = %s RETURNING id, title, release_date, album_name, genre;",
                    [
                        new_title,
                        new_release_date,
                        new_album_name,
                        new_genre,
                        modified,
                        id,
                    ],
                )
                updated_music = c.fetchone()

                if updated_music:
                    music_detail = {
                        "id": updated_music[0],
                        "title": updated_music[1],
                        "release_date": updated_music[2],
                        "album_name": updated_music[3],
                        "genre": updated_music[4],
                    }

                c.execute("DELETE FROM core_music_artists WHERE music_id = %s", [id])

                artist_names = []
                relation_id = uuid.uuid4()
                for artist_id in new_artist_ids:
                    c.execute(
                        "SELECT name FROM core_artistprofile WHERE id = %s;",
                        [artist_id],
                    )
                    artist_name = c.fetchone()[0]
                    artist_names.append(artist_name)

                    c.execute(
                        "INSERT INTO core_music_artists(id, music_id, artistprofile_id) VALUES (%s, %s, %s);",
                        [relation_id, id, artist_id],
                    )

                music_detail["artists"] = artist_names

                return Response(
                    {"message": "Music updated successfully", "music": music_detail},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"message": str(e)})

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@extend_schema(
    request=None,
    responses={
        (200, "application/json"): {"example": {"message": "Music deleted successfully"}},
        (405, "application/json"): {"example": {"message": "Invalid request method"}},
    },
)
@api_view(["DELETE"])
@permission_classes([permissions.IsAdminUser])
def delete_music(request: Request, id: str):
    """Delete existing music."""

    if request.method == "DELETE":
        with transaction.atomic(using=connection.alias), connection.cursor() as c:
            try:
                # Delete record from intermediatary table.
                c.execute(
                    "DELETE FROM core_music_artists WHERE music_id = %s;",
                    [id],
                )

                # Delete music from table.
                c.execute(
                    "DELETE FROM core_music WHERE id = %s;",
                    [id],
                )

                return Response(
                    {
                        "message": "Music deleted successfully.",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"message": str(e)})

    return Response(
        {"message": "Invaid request method."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )
