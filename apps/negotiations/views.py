from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import PriceNegotiation
from .serializers import (
    PriceNegotiationSerializer, PriceNegotiationCreateSerializer
)
from .permissions import IsNegotiationParticipant
from apps.services.models import ServiceRequest

class NegotiationListView(generics.ListAPIView):
    serializer_class = PriceNegotiationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        request_id = self.request.query_params.get('request_id')
        if request_id:
            return PriceNegotiation.objects.filter(service_request_id=request_id)
        return PriceNegotiation.objects.none()

class NegotiationCreateView(generics.CreateAPIView):
    serializer_class = PriceNegotiationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        negotiation = serializer.save(proposed_by=user)
        # Optionally: notify admin/client, set ServiceRequest.status = NEGOTIATING

class NegotiationAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        negotiation = get_object_or_404(PriceNegotiation, pk=pk)
        self.check_object_permissions(request, negotiation)
        negotiation.status = 'ACCEPTED'
        negotiation.save()
        # Optionally: update ServiceRequest status, notify parties
        return Response({'status': 'ACCEPTED'})

class NegotiationCounterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        negotiation = get_object_or_404(PriceNegotiation, pk=pk)
        self.check_object_permissions(request, negotiation)
        amount = request.data.get('proposed_amount')
        message = request.data.get('message')
        counter = PriceNegotiation.objects.create(
            service_request=negotiation.service_request,
            proposed_by=request.user,
            proposed_amount=amount,
            message=message,
            status='COUNTERED'
        )
        negotiation.status = 'COUNTERED'
        negotiation.save()
        # Optionally: notify parties
        return Response(PriceNegotiationSerializer(counter).data)