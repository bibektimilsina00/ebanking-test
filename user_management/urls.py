from django.urls import path
from .views import (
    UserListView,
    ResetPasswordView,
    SuspendUserView,
    ActivateUserView,
    CreateUserView,
    get_user_info,
    update_user,
    DeleteUserView,
)

urlpatterns = [
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("suspend-user/", SuspendUserView.as_view(), name="suspend_user"),
    path("activate-user/", ActivateUserView.as_view(), name="activate_user"),
    path("create-user/", CreateUserView.as_view(), name="create_user"),
    path("update-user/<int:user_id>/", update_user, name="update_user"),
    path("get_user_info/<int:user_id>/", get_user_info, name="get_user_info"),
    path("delete-user/", DeleteUserView.as_view(), name="delete_user"),
]
