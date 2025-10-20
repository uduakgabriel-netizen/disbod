# business/views.py
from rest_framework import serializers
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Business, BusinessVerificationRequest
from .serializers import BusinessSerializer, BusinessVerificationRequestSerializer


# ✅ List and create businesses
class BusinessListCreateView(generics.ListCreateAPIView):
    queryset = Business.objects.all().select_related('owner')
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Ensure one business per user
        if Business.objects.filter(owner=self.request.user).exists():
            raise serializers.ValidationError("You already have a registered business.")
        serializer.save(owner=self.request.user)


# ✅ Retrieve, update, delete a specific business
class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Business.objects.all().select_related('owner')
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        business = self.get_object()
        if business.owner != self.request.user:
            raise PermissionError("You can only update your own business.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionError("You can only delete your own business.")
        instance.delete()


# ✅ Request verification
class BusinessVerificationRequestCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            business = Business.objects.get(owner=request.user)
        except Business.DoesNotExist:
            return Response({'error': 'You do not have a business yet.'}, status=404)

        if hasattr(business, 'verification_request'):
            return Response({'error': 'Verification request already submitted.'}, status=400)

        serializer = BusinessVerificationRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(business=business)
            return Response({'message': 'Verification request submitted successfully.'})
        return Response(serializer.errors, status=400)


# ✅ Admin: Approve or reject verification requests
class BusinessVerificationApproveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        verification = get_object_or_404(BusinessVerificationRequest, pk=pk)
        verification.is_approved = True
        verification.reviewed_by = request.user
        verification.business.is_verified = True
        verification.business.save()
        verification.save()
        return Response({'message': f'{verification.business.name} has been verified successfully.'})
