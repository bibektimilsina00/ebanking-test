from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
import requests
import json
from organizations.models import Organization
from branches.models import Branch
from django.http import JsonResponse
from django.db import IntegrityError
from django.core.exceptions import ValidationError


from django.views.generic import TemplateView


def member_search(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({"error": f"Invalid JSON: {str(e)}"}, status=400)

    search_text = data.get("SearchText")
    if not search_text:
        return JsonResponse({"error": "Search text is required"}, status=400)

    try:
        organization = Organization.objects.get(owner=request.user)
    except Organization.DoesNotExist:
        return JsonResponse(
            {"error": "Organization associated with the current user does not exist"},
            status=404,
        )

    api_url = f"{organization.base_url}SearchMemberNameEbank"
    payload = {
        "clientId": organization.clint_id,
        "SearchText": search_text,
        "username": organization.username,
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
    except requests.exceptions.HTTPError as e:
        error_msg = (
            f"API responded with a non-successful status code: {e.response.status_code}"
        )
        return JsonResponse({"error": error_msg}, status=e.response.status_code)
    except requests.exceptions.ConnectionError:
        error_msg = "Failed to connect to the API endpoint."
        return JsonResponse({"error": error_msg}, status=503)
    except requests.exceptions.RequestException as e:
        error_msg = f"Error during API request: {str(e)}"

        return JsonResponse({"error": error_msg}, status=500)

    try:
        response_data = response.json()
    except json.JSONDecodeError:
        error_msg = "Failed to decode JSON from external API"
        return JsonResponse({"error": error_msg}, status=500)

    if response_data.get("isSuccess"):
        return JsonResponse(response_data)
    else:
        error_msg = "API did not return success"
        return JsonResponse({"error": error_msg}, status=400)


def member_ledger(request):
    if request.method == "POST":
        data = json.loads(request.body)
        memb_num = data.get("MembNum")
        try:
            organization = Organization.objects.get(owner=request.user)
        except Organization.DoesNotExist:
            return JsonResponse({"error": "Organization not found"}, status=404)

        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": memb_num,
            "username": organization.username,
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("isSuccess"):
                return JsonResponse(response_data)
            else:
                return JsonResponse(
                    {"error": "Failed to fetch data from external API"},
                    status=response.status_code,
                )
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def fetch_member_ledger(request):
    if request.method == "POST":
        json_data = json.loads(request.body)

        try:
            organization = Organization.objects.get(owner=request.user)

        except Organization.DoesNotExist:
            return JsonResponse({"error": "Organization not found"}, status=404)

        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": json_data.get("MembNum"),
            "username": organization.username,
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()
            if response.status_code == 200 and response_data.get("isSuccess"):
                return JsonResponse(response_data)
            else:
                return JsonResponse(
                    {"error": "Failed to fetch data from external API"},
                    status=response.status_code,
                )
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name="dispatch")
class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def post(self, request, *args, **kwargs):
        user = request.user
        user.first_name = request.POST.get("firstName", user.first_name)
        user.last_name = request.POST.get("lastName", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.phone = request.POST.get("phoneNumber", user.phone)
        user.address = request.POST.get("address", user.address)

        avatar_file = request.FILES.get("avtar")
        if avatar_file:
            user.avtar = avatar_file
        try:
            user.full_clean()  # This will check for any field errors according to the model's validation
            user.save()
            return JsonResponse(
                {"status": "success", "message": "Profile updated successfully"}
            )
        except ValidationError as e:
            errors = {field: error[0] for field, error in e.message_dict.items()}
            return JsonResponse(
                {"status": "error", "message": "Validation error", "errors": errors}
            )
        except IntegrityError as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Database error, possibly duplicate email",
                }
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )
