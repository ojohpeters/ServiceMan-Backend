from rest_framework import permissions

class IsNegotiationParticipant(permissions.BasePermission):
    """
    Only client, assigned serviceman, or admin can access negotiation.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.user_type == 'ADMIN':
            return True
        if obj.service_request.client == user:
            return True
        if obj.service_request.serviceman == user:
            return True
        return False