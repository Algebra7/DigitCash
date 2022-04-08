from .models import OTPLog
from django.db.models.base import ObjectDoesNotExist
from .models import SecretKey
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


def handle_otp(otp, email=False, phone=False):
    """
        This returns the time difference between OTP time stamp and the current time in minutes
        Params str:otp, str:email or str:phone
        Returns int
    """
    MAX_OTP_TIME = 15    #max time in minutes
    current_time = timezone.now()

    try:
        if phone:
            otp_record = OTPLog.objects.get(phone=phone)
        if email:
            otp_record = OTPLog.objects.get(email=email)

    except ObjectDoesNotExist:
        return {"state":"failed", "message":"OTP Verification failed. Invalid OTP. Please check and try again"}

    time_difference = current_time - otp_record.timestamp
    time_difference_minutes = time_difference.seconds / 60

    if time_difference_minutes >= MAX_OTP_TIME:
        #delete otp record
        otp_record.delete()
        return {"state":"failed", "message":"OTP Verification failed. OTP has expired. Please request for another one"}

    #delete otp record after verification to avoid reusing of the otp
    otp_record.delete()
    return {"state":"success", "message":"OTP verified successfully"}


def is_valid_secret_key(request):
    secret_key = request.headers.get('Secret-Key')
    if not secret_key:
        return False
    try:
        key = SecretKey.objects.get(key=secret_key)
    except ObjectDoesNotExist:
        return False

    return True
    