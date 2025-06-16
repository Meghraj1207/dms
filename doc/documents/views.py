from rest_framework import generics, permissions
from .models import Document
from .serializers import DocumentSerializer
from rest_framework.views import APIView
from .permissions import IsInitiator, IsReviewer, IsApprover, IsAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from utils.hashid import decode_id

class DocumentUploadView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    class DocumentCreateView(APIView):
        permission_classes = [IsAuthenticated, IsInitiator]  # only initiator can create

    class DocumentReviewView(APIView):
        permission_classes = [IsAuthenticated, IsReviewer]  # only reviewer can review

    class DocumentApprovalView(APIView):
        permission_classes = [IsAuthenticated, IsApprover]  # only approver can approve

    class AdminDocumentControlView(APIView):
        permission_classes = [IsAuthenticated, IsAdmin]  # only admin can delete/archive
    class DocumentView(APIView):
        permission_classes = [IsAuthenticated,IsAdmin]


class DocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, hashid):
        doc_id = decode_id(hashid)
        doc = get_object_or_404(Document, id=doc_id)

        serializer = DocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Review Document View

class DocumentReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReviewer]

    def post(self, request, hashid):
        doc_id = decode_id(hashid)
        doc = get_object_or_404(Document, id=doc_id)

        if doc.status != 'PENDING':
            return Response({'error': 'Document is already reviewed or processed.'}, status=status.HTTP_400_BAD_REQUEST)

        doc.status = 'REVIEWED'
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.save()
        return Response({'message': 'Document reviewed successfully'}, status=status.HTTP_200_OK)


class DocumentApprovalView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsApprover]

    def post(self, request, hashid):
        doc_id = decode_id(hashid)
        doc = get_object_or_404(Document, id=doc_id)

        if doc.status != 'REVIEWED':
            return Response({'error': 'Document must be reviewed before approval.'}, status=status.HTTP_400_BAD_REQUEST)

        doc.status = 'APPROVED'
        doc.approved_by = request.user
        doc.approved_at = timezone.now()
        doc.save()
        return Response({'message': 'Document approved successfully'}, status=status.HTTP_200_OK)