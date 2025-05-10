from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Escort, Subscription
from .forms import EscortForm
from django.core.paginator import Paginator
from django.utils import timezone
import requests
import json
import base64
from datetime import datetime
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm


def escort_dashboard(request):
    # Assuming the escort is related to the user
    escort = request.user.escort if hasattr(request.user, 'escort') else None
    return render(request, 'escort_dashboard.html', {'escort': escort})


@login_required
def escort_dashboard(request):
    return render(request, 'escort_dashboard.html')


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# M-PESA API Credentials (Replace with your own from Daraja API)
MPESA_CONSUMER_KEY = "e5kpRccaSHpkAsNX64FtGjORP7q2oTeuZCHA0QQbHVSuvTCh"  # Replace with your full Consumer Key
MPESA_CONSUMER_SECRET = "TR5ATBchQEXFVyheJgi3GwbMYQbUxaTfL3CDHNFDnbK5gzTeAVnusOpePaVLYVKC"  # Replace with your full Consumer Secret
MPESA_SHORTCODE = "174379"  # Use default sandbox shortcode unless 9009227 is confirmed
MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # Replace with your passkey
MPESA_CALLBACK_URL = "https://yourdomain.com/payment/callback/"  # Replace with a publicly accessible URL (e.g., ngrok)

def get_mpesa_access_token():
    if MPESA_CONSUMER_KEY == "e5kpRccaSHpkAsNX64FtGjORP7q2oTeuZCHA0QQbHVSuvTCh" or MPESA_CONSUMER_SECRET == "TR5ATBchQEXFVyheJgi3GwbMYQbUxaTfL3CDHNFDnbK5gzTeAVnusOpePaVLYVKC":
        logger.error("M-PESA credentials are not set. Please update MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET.")
        raise ValueError("M-PESA credentials are not configured. Please set MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET.")

    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {"Authorization": "Basic " + base64.b64encode(f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}".encode()).decode()}
    try:
        response = requests.get(api_url, headers=headers)
        logger.debug(f"M-PESA OAuth response status: {response.status_code}")
        logger.debug(f"M-PESA OAuth response headers: {response.headers}")
        logger.debug(f"M-PESA OAuth response text: {response.text}")
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 400, 401)
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get M-PESA access token: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Failed to parse M-PESA response as JSON: {str(e)}")
        raise

def initiate_mpesa_payment(phone_number, amount, account_reference):
    try:
        access_token = get_mpesa_access_token()
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()
        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",  # For Buy Goods (Till Number)
            "Amount": amount,
            "PartyA": phone_number,  # Format: 2547XXXXXXXX
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": "Escort Subscription Payment"
        }
        response = requests.post(api_url, json=payload, headers=headers)
        logger.debug(f"M-PESA STK Push response status: {response.status_code}")
        logger.debug(f"M-PESA STK Push response headers: {response.headers}")
        logger.debug(f"M-PESA STK Push response text: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to initiate M-PESA payment: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Failed to parse M-PESA STK Push response as JSON: {str(e)}")
        raise

@login_required
def escort_create(request):
    if request.method == 'POST':
        form = EscortForm(request.POST, request.FILES)
        if form.is_valid():
            escort = form.save(commit=False)
            escort.user = request.user
            escort.is_active = False  # Initially inactive until payment is confirmed
            escort.save()
            # Format phone number to 2547XXXXXXXX
            phone_number = escort.phone_number
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                messages.error(request, "Phone number must be in the format 2547XXXXXXXX or 07XXXXXXXX.")
                return render(request, 'directory/escort_create.html', {'form': form})
            amount = "499"
            account_reference = f"ESCORT-{escort.id}"
            try:
                payment_response = initiate_mpesa_payment(phone_number, amount, account_reference)
                if payment_response.get("ResponseCode") == "0":
                    return render(request, 'directory/payment_pending.html', {'escort': escort})
                else:
                    # If payment initiation fails, delete the escort or keep it inactive
                    escort.delete()
                    messages.error(request, "Payment initiation failed. Please try again.")
                    return render(request, 'directory/escort_create.html', {'form': form})
            except Exception as e:
                logger.error(f"Error during payment initiation: {str(e)}")
                # Delete the escort if payment fails
                escort.delete()
                messages.error(request, f"Payment initiation failed: {str(e)}")
                return render(request, 'directory/escort_create.html', {'form': form})
    else:
        form = EscortForm()
    return render(request, 'directory/escort_create.html', {'form': form})

def payment_callback(request):
    # Process M-PESA callback (called by Safaricom)
    try:
        data = json.loads(request.body)
        if data["Body"]["stkCallback"]["ResultCode"] == 0:
            checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
            amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
            phone_number = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
            account_reference = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"]
            escort_id = account_reference.split('-')[1]
            escort = get_object_or_404(Escort, id=escort_id)
            # Create Subscription
            subscription = Subscription.objects.create(
                escort=escort,
                amount=amount,
                is_active=True
            )
            # Activate the escort profile
            escort.is_active = True
            escort.save()
            return HttpResponse("Payment successful")
        else:
            # If payment fails, keep the escort inactive or delete it
            account_reference = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"]
            escort_id = account_reference.split('-')[1]
            escort = get_object_or_404(Escort, id=escort_id)
            escort.delete()  # Optional: Delete if payment fails
            return HttpResponse("Payment failed")
    except Exception as e:
        logger.error(f"Error in payment callback: {str(e)}")
        return HttpResponse("Payment callback processing failed")

def escort_list(request):
    query = request.GET.get('q')
    if query:
        escorts = Escort.objects.filter(is_active=True).filter(name__icontains=query) | Escort.objects.filter(is_active=True).filter(city__icontains=query)
    else:
        escorts = Escort.objects.filter(is_active=True)
    escorts = escorts.order_by('name')  # Ensure consistent ordering for pagination
    paginator = Paginator(escorts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'directory/escort_list.html', {'page_obj': page_obj})

def escort_detail(request, pk):
    escort = get_object_or_404(Escort, pk=pk)
    if not escort.is_active:
        messages.error(request, "This escort profile is not active.")
        return redirect('escort_list')
    subscription = Subscription.objects.filter(escort=escort, is_active=True).first()
    if subscription:
        subscription.check_status()  # Check if subscription is still active
    show_details = subscription and subscription.is_active
    return render(request, 'directory/escort_detail.html', {'escort': escort, 'show_details': show_details})



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def edit_escort_profile(request):
    escort = get_object_or_404(Escort, user=request.user)
    if not escort.is_active:
        messages.error(request, "This escort profile is not active.")
        return redirect('escort_list')
    if request.method == 'POST':
        form = EscortForm(request.POST, request.FILES, instance=escort)
        if form.is_valid():
            form.save()
            return redirect('escort_detail', pk=escort.pk)
    else:
        form = EscortForm(instance=escort)
    return render(request, 'directory/edit_escort_profile.html', {'form': form, 'escort': escort})