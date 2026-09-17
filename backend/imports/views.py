"""API view for bulk roster upload."""

from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from imports.serializers import RosterUploadSerializer
from imports.services import RosterUploadError, import_roster


class RosterUploadView(APIView):
    """Accepts a multipart .xlsx roster; all-or-nothing, with row-level errors on failure."""

    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = RosterUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = import_roster(serializer.validated_data["file"])
        except RosterUploadError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_201_CREATED)
