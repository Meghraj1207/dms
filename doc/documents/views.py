from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Document
from .serializers import DocumentSerializer
from .permissions import IsInitiator, IsReviewer, IsApprover, IsAdmin
from utils.hashid import decode_id


class DocumentUploadView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, IsInitiator]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class DocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hashid):
        doc_id = decode_id(hashid)
        doc = get_object_or_404(Document, id=doc_id)

        if request.user.role == 'viewer' and doc.status != 'APPROVED':
            return Response({'error': 'You are only allowed to view approved documents.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = DocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocumentReviewView(APIView):
    permission_classes = [IsAuthenticated, IsReviewer]

    def post(self, request, hashid):
        doc_id = decode_id(hashid)
        doc = get_object_or_404(Document, id=doc_id)

        if doc.status != 'PENDING':
            return Response({'error': 'Document is already reviewed or processed.'},
                            status=status.HTTP_400_BAD_REQUEST)

        doc.status = 'REVIEWED'
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.save()
        return Response({'message': 'Document reviewed successfully'}, status=status.HTTP_200_OK)


class DocumentApprovalView(APIView):
    permission_classes = [IsAuthenticated, IsApprover]

    def post(self, request, hashid):
        doc_id = decode_id(hashid)
        doc = get_object_or_404(Document, id=doc_id)

        if doc.status != 'REVIEWED':
            return Response({'error': 'Document must be reviewed before approval.'},
                            status=status.HTTP_400_BAD_REQUEST)

        doc.status = 'APPROVED'
        doc.approved_by = request.user
        doc.approved_at = timezone.now()
        doc.save()
        return Response({'message': 'Document approved successfully'}, status=status.HTTP_200_OK)


class AdminDocumentControlView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, hashid):
        doc_id = decode_id(hashid)
        doc = get_object_or_404(Document, id=doc_id)
        doc.delete()
        return Response({'message': 'Document deleted'}, status=status.HTTP_204_NO_CONTENT)
