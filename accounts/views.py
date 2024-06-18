from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
import requests
import json
from organizations.models import Organization
from branches.models import Branch

@csrf_exempt
def member_search(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        search_text = data.get('SearchText')
        try:
            organization = Organization.objects.get(owner=request.user)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organization not found'}, status=404)

        api_url = f"{organization.base_url}SearchMemberNameEbank"
        payload = {
            "clientId": organization.clint_id,
            "SearchText": search_text,
            "username": organization.username
        }

        try:
            response = requests.post(api_url, json=payload)
            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)

            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                print("Response content:", response.content)
                return JsonResponse({'error': 'Invalid response from external API'}, status=500)

            if response_data.get('isSuccess'):
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)
        except requests.RequestException as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
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
