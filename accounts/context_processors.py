from .models import Account



def account_info(request):
    return {
        'accounts': Account.objects.filter(account_holder=request.user)
    }
def user_info(request):
    return {
        'user': request.user
    }
