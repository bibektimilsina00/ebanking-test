from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
import requests
import json
from organizations.models import Organization
from branches.models import Branch


def member_search(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

    search_text = data.get('SearchText')
    if not search_text:
        return JsonResponse({'error': 'Search text is required'}, status=400)

    try:
        organization = Organization.objects.get(owner=request.user)
    except Organization.DoesNotExist:
        return JsonResponse({'error': 'Organization associated with the current user does not exist'}, status=404)

    api_url = f"{organization.base_url}SearchMemberNameEbank"
    payload = {
        "clientId": organization.client_id,
        "SearchText": search_text,
        "username": organization.username
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
    except requests.exceptions.HTTPError as e:
        error_msg = f'API responded with a non-successful status code: {e.response.status_code}'
        print(error_msg, "Response:", e.response.text)
        return JsonResponse({'error': error_msg}, status=e.response.status_code)
    except requests.exceptions.ConnectionError:
        error_msg = 'Failed to connect to the API endpoint.'
        print(error_msg, f"URL attempted: {api_url}")
        return JsonResponse({'error': error_msg}, status=503)
    except requests.exceptions.RequestException as e:
        error_msg = f'Error during API request: {str(e)}'
        print(error_msg)
        return JsonResponse({'error': error_msg}, status=500)

    try:
        response_data = response.json()
    except json.JSONDecodeError:
        error_msg = 'Failed to decode JSON from external API'
        print(error_msg, "Response content:", response.content)
        return JsonResponse({'error': error_msg}, status=500)

    if response_data.get('isSuccess'):
        return JsonResponse(response_data)
    else:
        error_msg = 'API did not return success'
        print(error_msg, "API response:", response_data)
        return JsonResponse({'error': error_msg}, status=400)




def member_ledger(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        memb_num = data.get('MembNum')
        try:
            organization = Organization.objects.get(owner=request.user)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organization not found'}, status=404)

        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": memb_num,
            "username": organization.username
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('isSuccess'):
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)
        except requests.RequestException as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def fetch_member_ledger(request):
    if request.method == 'POST':
        try:
            branch = Branch.objects.get(owner=request.user)
            organization = branch.organization
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organization not found'}, status=404)

        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": branch.member_number,
            "username": organization.username
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()
            if response.status_code == 200 and response_data.get('isSuccess'):
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
