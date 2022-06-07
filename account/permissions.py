from django.db.models.base import ObjectDoesNotExist
from rest_framework import permissions
from account.models import SecretKey


class IsSecretKeyProvided(permissions.BasePermission):
  message = "You're not allowed to access this resource! Please provide a valid secret key"

  def has_permission(self, request, view):
    secret_key = request.headers.get('Secret-Key')
    if not secret_key:
      return False
    try:
      key = SecretKey.objects.get(key=secret_key)
    except ObjectDoesNotExist:
      return False
    return True
