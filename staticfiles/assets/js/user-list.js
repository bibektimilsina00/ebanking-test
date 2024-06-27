
    let actionUrl = '';
    let actionData = {};

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showModal(url, data, message) {
        actionUrl = url;
        actionData = data;
        document.querySelector('#actionModal .modal-body').innerText = message;
        const actionModal = new bootstrap.Modal(document.getElementById('actionModal'), {});
        actionModal.show();
    }

    document.getElementById('confirmActionButton').addEventListener('click', function() {
        showBaseModal(true);
        actionData['csrfmiddlewaretoken'] = getCsrfToken();
        $.ajax({
            type: 'POST',
            url: actionUrl,
            data: actionData,
            success: function(response) {
                alert(response.message);
                showBaseModal(false);
                location.reload();  // Reload the page to reflect changes
            },
            error: function(response) {
                showModal(false);
                alert('Error: ' + response.responseText);
            }
        });
    });

    function resetPassword(userId) {
        const resetPasswordUrl = '/users/reset-password/'; // Static URL
        showModal(
            resetPasswordUrl, 
            {
                'user_id': userId
            }, 
            'Are you sure you want to reset the password for this user?'
        );
    }

    function suspendUser(userId) {
        const suspendUserUrl = '/users/suspend-user/'; // Static URL
        showModal(
            suspendUserUrl, 
            {
                'user_id': userId
            }, 
            'Are you sure you want to suspend this user?'
        );
    }

    function activateUser(userId) {
        const activateUserUrl = '/users/activate-user/'; // Static URL
        showModal(
            activateUserUrl, 
            {
                'user_id': userId
            }, 
            'Are you sure you want to activate this user?'
        );
    }


