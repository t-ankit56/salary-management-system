"""Serializer for the roster upload endpoint."""

from rest_framework import serializers


class RosterUploadSerializer(serializers.Serializer):
    """Wraps the uploaded multipart file field."""

    file = serializers.FileField()
