from django.urls import path
from .views import DocumentUploadView, DocumentReviewView, DocumentApprovalView, DocumentView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('<str:hashid>/view/', DocumentView.as_view(), name='document_view'),
    path('<str:hashid>/review/', DocumentReviewView.as_view(), name='review_document'),
    path('<str:hashid>/approve/', DocumentApprovalView.as_view(), name='approve_document')
]