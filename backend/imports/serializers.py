from rest_framework import serializers


class RosterUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
