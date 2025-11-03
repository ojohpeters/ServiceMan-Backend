"""
Professional Service Request Workflow Views

Complete workflow with admin as the bridge between client and serviceman.
All communication flows through admin with notifications at every step.

Workflow:
1. Client creates request → Admin notified
2. Admin assigns serviceman → Serviceman & Client notified
3. Serviceman submits estimate → Admin notified
4. Admin finalizes price → Client notified
5. Client pays → Admin notified
6. Admin authorizes work → Serviceman notified
7. Serviceman completes job → Admin notified
8. Admin confirms to client → Client notified
9. Client rates serviceman → Serviceman & Admin notified
"""

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from decimal import Decimal
import logging

from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from apps.notifications.models import Notification
from apps.users.models import ServicemanProfile

User = get_user_model()
logger = logging.getLogger(__name__)


def notify_admins(title, message, service_request=None):
    """Send notification to all admins"""
    admins = User.objects.filter(user_type='ADMIN')
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title=title,
            message=message,
            notification_type='ADMIN_ALERT',
            service_request=service_request
        )
    logger.info(f"Notified {admins.count()} admin(s): {title}")


def notify_user(user, title, message, notification_type='GENERAL', service_request=None):
    """Send notification to a specific user"""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        service_request=service_request
    )
    logger.info(f"Notified {user.username}: {title}")


# ============================================================================
# STEP 3: SERVICEMAN SUBMITS COST ESTIMATE
# ============================================================================

class ServicemanSubmitEstimateView(APIView):
    """
    Serviceman submits cost estimate after site inspection.
    
    - Only assigned serviceman can submit
    - Status must be PENDING_ESTIMATION
    - Admin is notified
    - Status changes to ESTIMATION_SUBMITTED
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'estimated_cost': {
                        'type': 'number',
                        'description': 'Serviceman estimated cost for the job'
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Optional notes about the estimate'
                    }
                },
                'required': ['estimated_cost']
            }
        },
        responses={
            200: OpenApiResponse(description="Estimate submitted successfully"),
            400: OpenApiResponse(description="Invalid request"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Service request not found")
        }
    )
    def post(self, request, pk):
        if request.user.user_type != 'SERVICEMAN':
            return Response(
                {'error': 'Only servicemen can submit estimates'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify this serviceman is assigned
        if service_request.serviceman != request.user:
            return Response(
                {'error': 'You are not assigned to this service request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify status
        if service_request.status != 'PENDING_ESTIMATION':
            return Response(
                {'error': f'Cannot submit estimate. Current status: {service_request.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimated_cost = request.data.get('estimated_cost')
        notes = request.data.get('notes', '')
        
        if not estimated_cost:
            return Response(
                {'error': 'estimated_cost is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            estimated_cost = Decimal(str(estimated_cost))
            if estimated_cost <= 0:
                raise ValueError("Cost must be positive")
        except (ValueError, decimal.InvalidOperation) as e:
            return Response(
                {'error': f'Invalid estimated_cost: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update service request
        with transaction.atomic():
            service_request.serviceman_estimated_cost = estimated_cost
            service_request.status = 'ESTIMATION_SUBMITTED'
            service_request.save()
            
            # Notify admin
            notify_admins(
                title=f"Cost Estimate Submitted - Request #{service_request.id}",
                message=f"Serviceman {request.user.get_full_name()} submitted cost estimate of ₦{estimated_cost:,.2f} for service request #{service_request.id}. Please review and add platform fee.{f' Notes: {notes}' if notes else ''}",
                service_request=service_request
            )
        
        serializer = ServiceRequestSerializer(service_request)
        return Response({
            'message': 'Estimate submitted successfully. Admin will review and finalize pricing.',
            'service_request': serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================================
# STEP 4: ADMIN FINALIZES PRICE WITH PLATFORM FEE
# ============================================================================

class AdminFinalizePriceView(APIView):
    """
    Admin adds platform fee and finalizes price for client.
    
    - Only admin can finalize
    - Status must be ESTIMATION_SUBMITTED
    - Client is notified
    - Status changes to AWAITING_CLIENT_APPROVAL
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'markup_percentage': {
                        'type': 'number',
                        'description': 'Platform fee percentage (default 10%)'
                    },
                    'admin_notes': {
                        'type': 'string',
                        'description': 'Optional notes for the client'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Price finalized successfully"),
            400: OpenApiResponse(description="Invalid request"),
            403: OpenApiResponse(description="Admin only"),
            404: OpenApiResponse(description="Service request not found")
        }
    )
    def post(self, request, pk):
        if request.user.user_type != 'ADMIN':
            return Response(
                {'error': 'Only administrators can finalize pricing'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify status
        if service_request.status != 'ESTIMATION_SUBMITTED':
            return Response(
                {'error': f'Cannot finalize price. Current status: {service_request.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not service_request.serviceman_estimated_cost:
            return Response(
                {'error': 'Serviceman estimate not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        markup_percentage = request.data.get('markup_percentage', 10.00)
        admin_notes = request.data.get('admin_notes', '')
        
        try:
            markup_percentage = Decimal(str(markup_percentage))
            if markup_percentage < 0 or markup_percentage > 100:
                raise ValueError("Markup must be between 0 and 100")
        except (ValueError, decimal.InvalidOperation) as e:
            return Response(
                {'error': f'Invalid markup_percentage: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate final cost
        base_cost = service_request.serviceman_estimated_cost
        platform_fee = base_cost * (markup_percentage / 100)
        final_cost = base_cost + platform_fee
        
        # Update service request
        with transaction.atomic():
            service_request.admin_markup_percentage = markup_percentage
            service_request.final_cost = final_cost
            service_request.status = 'AWAITING_CLIENT_APPROVAL'
            service_request.save()
            
            # Notify client
            notify_user(
                user=service_request.client,
                title=f"Price Ready for Your Approval - Request #{service_request.id}",
                message=f"Your service request has been priced:\n\n"
                       f"• Service Cost: ₦{base_cost:,.2f}\n"
                       f"• Platform Fee ({markup_percentage}%): ₦{platform_fee:,.2f}\n"
                       f"• Total Amount: ₦{final_cost:,.2f}\n\n"
                       f"Please review and proceed with payment to confirm the job.{f' {admin_notes}' if admin_notes else ''}",
                notification_type='PAYMENT_REQUEST',
                service_request=service_request
            )
        
        serializer = ServiceRequestSerializer(service_request)
        return Response({
            'message': 'Price finalized and sent to client for approval',
            'service_request': serializer.data,
            'pricing_breakdown': {
                'base_cost': float(base_cost),
                'platform_fee': float(platform_fee),
                'markup_percentage': float(markup_percentage),
                'final_cost': float(final_cost)
            }
        }, status=status.HTTP_200_OK)


# ============================================================================
# STEP 6: ADMIN AUTHORIZES WORK TO BEGIN
# ============================================================================

class AdminAuthorizeWorkView(APIView):
    """
    Admin authorizes serviceman to begin work after client payment.
    
    - Only admin can authorize
    - Status must be PAYMENT_COMPLETED
    - Serviceman is notified
    - Status changes to IN_PROGRESS
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'instructions': {
                        'type': 'string',
                        'description': 'Optional instructions for the serviceman'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Work authorized successfully"),
            400: OpenApiResponse(description="Invalid request"),
            403: OpenApiResponse(description="Admin only"),
            404: OpenApiResponse(description="Service request not found")
        }
    )
    def post(self, request, pk):
        if request.user.user_type != 'ADMIN':
            return Response(
                {'error': 'Only administrators can authorize work'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify status
        if service_request.status != 'PAYMENT_COMPLETED':
            return Response(
                {'error': f'Cannot authorize work. Current status: {service_request.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not service_request.serviceman:
            return Response(
                {'error': 'No serviceman assigned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instructions = request.data.get('instructions', '')
        
        # Update service request
        with transaction.atomic():
            service_request.status = 'IN_PROGRESS'
            service_request.save()
            
            # Notify serviceman
            notify_user(
                user=service_request.serviceman,
                title=f"Work Authorized - Request #{service_request.id}",
                message=f"Payment confirmed! You are authorized to begin work on service request #{service_request.id}.\n\n"
                       f"Client: {service_request.client.get_full_name()}\n"
                       f"Phone: {service_request.client.phone_number if hasattr(service_request.client, 'phone_number') else 'N/A'}\n"
                       f"Address: {service_request.client_address}\n"
                       f"Job Amount: ₦{service_request.final_cost:,.2f}{f'\n\nInstructions: {instructions}' if instructions else ''}",
                notification_type='JOB_ASSIGNED',
                service_request=service_request
            )
            
            # Also notify client
            notify_user(
                user=service_request.client,
                title=f"Work Has Begun - Request #{service_request.id}",
                message=f"Your service request is now in progress. The serviceman will contact you shortly to complete the work.",
                notification_type='STATUS_UPDATE',
                service_request=service_request
            )
        
        serializer = ServiceRequestSerializer(service_request)
        return Response({
            'message': 'Work authorized. Serviceman has been notified to begin.',
            'service_request': serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================================
# STEP 7: SERVICEMAN MARKS JOB COMPLETE
# ============================================================================

class ServicemanCompleteJobView(APIView):
    """
    Serviceman marks job as completed.
    
    - Only assigned serviceman can complete
    - Status must be IN_PROGRESS
    - Admin is notified
    - Status changes to COMPLETED (waiting for admin confirmation)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'completion_notes': {
                        'type': 'string',
                        'description': 'Notes about the completed work'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Job marked as complete"),
            400: OpenApiResponse(description="Invalid request"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Service request not found")
        }
    )
    def post(self, request, pk):
        if request.user.user_type != 'SERVICEMAN':
            return Response(
                {'error': 'Only servicemen can complete jobs'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify this serviceman is assigned
        if service_request.serviceman != request.user:
            return Response(
                {'error': 'You are not assigned to this service request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify status
        if service_request.status != 'IN_PROGRESS':
            return Response(
                {'error': f'Cannot mark as complete. Current status: {service_request.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        completion_notes = request.data.get('completion_notes', '')
        
        # Update service request
        with transaction.atomic():
            from django.utils import timezone
            service_request.status = 'COMPLETED'
            service_request.work_completed_at = timezone.now()
            service_request.save()
            
            # Update serviceman stats
            try:
                profile = request.user.serviceman_profile
                profile.total_jobs_completed = (profile.total_jobs_completed or 0) + 1
                profile.save(update_fields=['total_jobs_completed'])
            except:
                pass
            
            # Notify admin
            notify_admins(
                title=f"Job Completed - Request #{service_request.id}",
                message=f"Serviceman {request.user.get_full_name()} has marked service request #{service_request.id} as completed. Please verify and notify the client.{f' Completion Notes: {completion_notes}' if completion_notes else ''}",
                service_request=service_request
            )
        
        serializer = ServiceRequestSerializer(service_request)
        return Response({
            'message': 'Job marked as complete. Admin will verify and notify the client.',
            'service_request': serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================================
# STEP 8: ADMIN CONFIRMS COMPLETION TO CLIENT
# ============================================================================

class AdminConfirmCompletionView(APIView):
    """
    Admin confirms job completion to client.
    
    - Only admin can confirm
    - Status must be COMPLETED
    - Client is notified
    - Status remains COMPLETED (awaiting client review)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'message_to_client': {
                        'type': 'string',
                        'description': 'Optional message for the client'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Completion confirmed to client"),
            400: OpenApiResponse(description="Invalid request"),
            403: OpenApiResponse(description="Admin only"),
            404: OpenApiResponse(description="Service request not found")
        }
    )
    def post(self, request, pk):
        if request.user.user_type != 'ADMIN':
            return Response(
                {'error': 'Only administrators can confirm completion'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify status
        if service_request.status != 'COMPLETED':
            return Response(
                {'error': f'Cannot confirm completion. Current status: {service_request.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message_to_client = request.data.get('message_to_client', '')
        
        # Notify client
        with transaction.atomic():
            notify_user(
                user=service_request.client,
                title=f"Job Completed - Request #{service_request.id}",
                message=f"Great news! Your service request has been completed successfully.\n\n"
                       f"Serviceman: {service_request.serviceman.get_full_name()}\n"
                       f"Category: {service_request.category.name}\n\n"
                       f"Please take a moment to rate your experience and help us improve our service.{f'\n\n{message_to_client}' if message_to_client else ''}",
                notification_type='JOB_COMPLETED',
                service_request=service_request
            )
        
        serializer = ServiceRequestSerializer(service_request)
        return Response({
            'message': 'Client has been notified of job completion',
            'service_request': serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================================
# STEP 9: CLIENT SUBMITS RATING & REVIEW
# ============================================================================

class ClientSubmitReviewView(APIView):
    """
    Client submits rating and optional review for serviceman.
    
    - Only the client can submit review
    - Status must be COMPLETED
    - Serviceman & Admin are notified
    - Status changes to CLIENT_REVIEWED
    - Serviceman rating is updated
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'rating': {
                        'type': 'integer',
                        'description': 'Rating from 1 to 5 stars',
                        'minimum': 1,
                        'maximum': 5
                    },
                    'review': {
                        'type': 'string',
                        'description': 'Optional written review'
                    }
                },
                'required': ['rating']
            }
        },
        responses={
            200: OpenApiResponse(description="Review submitted successfully"),
            400: OpenApiResponse(description="Invalid request"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Service request not found")
        }
    )
    def post(self, request, pk):
        if request.user.user_type != 'CLIENT':
            return Response(
                {'error': 'Only clients can submit reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify this is the client's request
        if service_request.client != request.user:
            return Response(
                {'error': 'This is not your service request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify status
        if service_request.status != 'COMPLETED':
            return Response(
                {'error': f'Cannot submit review. Current status: {service_request.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating = request.data.get('rating')
        review_text = request.data.get('review', '')
        
        if not rating:
            return Response(
                {'error': 'rating is required (1-5)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid rating: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update serviceman rating
        with transaction.atomic():
            service_request.status = 'CLIENT_REVIEWED'
            service_request.save()
            
            # Update serviceman profile rating
            if service_request.serviceman:
                try:
                    profile = service_request.serviceman.serviceman_profile
                    current_rating = profile.rating or Decimal('0.00')
                    total_jobs = profile.total_jobs_completed or 0
                    
                    # Calculate new average rating
                    if total_jobs > 0:
                        new_rating = ((current_rating * (total_jobs - 1)) + Decimal(str(rating))) / total_jobs
                        profile.rating = round(new_rating, 2)
                        profile.save(update_fields=['rating'])
                except Exception as e:
                    logger.error(f"Error updating serviceman rating: {str(e)}")
            
            # Notify serviceman
            if service_request.serviceman:
                stars = '⭐' * rating
                notify_user(
                    user=service_request.serviceman,
                    title=f"New Review - {stars}",
                    message=f"You received a {rating}-star rating from {service_request.client.get_full_name()} for service request #{service_request.id}.{f' Review: {review_text}' if review_text else ''}",
                    notification_type='REVIEW_RECEIVED',
                    service_request=service_request
                )
            
            # Notify admin
            notify_admins(
                title=f"Client Review Submitted - Request #{service_request.id}",
                message=f"Client {service_request.client.get_full_name()} rated serviceman {service_request.serviceman.get_full_name() if service_request.serviceman else 'N/A'} {rating}/5 stars.{f' Review: {review_text}' if review_text else ''}",
                service_request=service_request
            )
        
        serializer = ServiceRequestSerializer(service_request)
        return Response({
            'message': 'Thank you for your review! Your feedback helps us improve.',
            'service_request': serializer.data,
            'rating': rating
        }, status=status.HTTP_200_OK)
