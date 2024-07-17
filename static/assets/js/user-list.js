// Utility Functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showBaseModal(show) {
    // Placeholder for showing or hiding a loading modal based on 'show' boolean
    console.log(show ? "Show Loader" : "Hide Loader");
}

// Handle Fetch Requests with Error Handling
function handleFetchRequest(url, method, body) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(body)
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    });
}

// Handle Errors and Display Messages
function handleError(error, customMessage = "An error occurred") {
    console.error(customMessage, error);
    alert(customMessage + ": " + error);
    showBaseModal(false); // Hide loader on error
}

// Show Modal with Action Confirmation
function showModal(url, data, message) {
    actionUrl = url;
    actionData = data;
    document.querySelector('#actionModal .modal-body').innerText = message;
    const actionModal = new bootstrap.Modal(document.getElementById('actionModal'), {});
    actionModal.show();
}

// Event Listeners for User Actions
document.getElementById('confirmActionButton').addEventListener('click', function () {

    handleFetchRequest(actionUrl, 'POST', actionData)
        .then(data => {
            alert(data.message);
            location.reload(); // Reload the page to reflect changes
        })
        .catch(error => handleError(error, 'Error performing action'));
});

// User Action Functions
function resetPassword(userId) {
    showUserActionModal(userId, 'resetPassword');
}

function suspendUser(userId) {
    showUserActionModal(userId, 'suspendUser');
}

function deleteUser(userId) {
    showUserActionModal(userId, 'deleteUser');
}

function activateUser(userId) {
    showUserActionModal(userId, 'activateUser');
}

function showUserActionModal(userId, actionType) {
    const urlMap = {
        'resetPassword': '/users/reset-password/',
        'suspendUser': '/users/suspend-user/',
        'deleteUser': '/users/delete-user/',
        'activateUser': '/users/activate-user/'
    };
    const messagesMap = {
        'resetPassword': 'Are you sure you want to reset the password for this user?',
        'suspendUser': 'Are you sure you want to suspend this user?',
        'deleteUser': 'Are you sure you want to delete this user?',
        'activateUser': 'Are you sure you want to activate this user?'
    };
    showModal(urlMap[actionType], { 'user_id': userId }, messagesMap[actionType]);
}





// Fetching Member Details and Display Suggestions
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-member');
    const suggestionsBox = document.createElement('div');
    suggestionsBox.classList.add('suggestions-box');
    searchInput.parentNode.appendChild(suggestionsBox);

    searchInput.addEventListener('input', function () {
        const searchText = this.value.trim(); // Trim whitespace from input

        if (!searchText) {
            suggestionsBox.innerHTML = ''; // Clear suggestions if input is empty
            return; // Exit the function if searchText is empty
        }



        handleFetchRequest('/accounts/member-search/', 'POST', { SearchText: this.value })
            .then(data => {
                if (data.isSuccess) {
                    const members = JSON.parse(data.result);
                    displaySuggestions(members);
                } else {
                    console.error('Failed to fetch members:', data);
                }
            })
            .catch(error => handleError(error, 'Error fetching members'))
            .finally(() => showBaseModal(false));
    });

    function displaySuggestions(members) {
        suggestionsBox.innerHTML = '';
        members.forEach(member => {
            const suggestionItem = document.createElement('div');
            suggestionItem.classList.add('suggestion-item');
            suggestionItem.classList.add('list-group-item', 'list-group-item-action', 'd-flex', 'justify-content-between', 'align-items-center', 'my-2', 'rounded');
            suggestionItem.textContent = `${member.MemberName} | ${member.MemberNum}`;
            suggestionItem.onclick = () => {
                fetchMemberLedger(member);
                suggestionsBox.innerHTML = ''; // Clear suggestions
            };
            suggestionsBox.appendChild(suggestionItem);
        });
    }

    function fetchMemberLedger(member) {



        handleFetchRequest('/accounts/member-ledger/', 'POST', { MembNum: member.MemberID })
            .then(data => {
                if (data.isSuccess) {

                    displayAccountList(JSON.parse(data.result));
                    fillFormWithMemberData(member);
                } else {
                    console.error('Failed to fetch member ledger:', data);
                }
            })
            .catch(error => handleError(error, 'Error fetching member ledger'));
    }

    function fillFormWithMemberData(member) {
        document.getElementById('add-user-firstname').value = member.MemberName.split(' ')[0];
        document.getElementById('add-user-lastname').value = member.MemberName.split(' ').slice(1).join(' ');;
        document.getElementById('add-user-email').value = member.Email || '';
        document.getElementById('add-user-contact').value = member.Mobile || '';
        document.getElementById('add-user-member-number').value = member.MemberID || '';
        // Additional fields as needed
    }

});

// Additional Placeholder Functions
function displayAccountList(accounts) {
    const accountList = document.getElementById('account-list');
    accountList.innerHTML = ''; // Clear existing content

    accounts.forEach(account => {
        const accountItem = document.createElement('div');
        accountItem.classList.add('mb-3', 'p-2', 'border', 'rounded');
        accountItem.classList.add('account-item');
        accountItem.innerHTML = `

          <div class="form-check">
                <input type="checkbox" class="form-check-input"  id="account-${account.AccountNo}" name="accounts" value="${account.AccNum}">
                <label class="form-check-label" for="account-${account.AccountNo}">
                    ${account.GroupName} - ${account.AccNum} 
                </label>
            </div>`;

        accountList.appendChild(accountItem);
    });
}


// Helper function to get a cookie by name, useful for CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}






// Fetch and display accounts when the form is opened for branch/member roles
const offcanvasAddUser = document.getElementById('offcanvasAddUser');



searchInput = document.getElementById('search-member');
offcanvasAddUser.addEventListener('shown.bs.offcanvas', function () {

    if (!searchInput) {
        fetchAccountDetailsForStaff();
    }
});
function fetchAccountDetailsForStaff() {


    fetch('/accounts/fetch-member-ledger/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({})
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.isSuccess) {
                displayAccountList(data.result); // Pass only the result part which is the array
            } else {
                throw new Error("Failed to fetch accounts: " + data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching or parsing accounts:', error);
            showBaseModal(false);
        })
        .finally(() => {
            showBaseModal(false); // Hide loading modal in any case
        });
}

function showUserEditCanvas(userId) {
    fetch(`/users/get_user_info/${userId}/`, {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
        .then(response => response.json())
        .then(userData => {
            if (userData.status === 'success') {

                // Set form values
                document.getElementById('edit-user-firstname').value = userData.data.first_name;
                document.getElementById('edit-user-lastname').value = userData.data.last_name;
                document.getElementById('edit-user-email').value = userData.data.email;
                document.getElementById('edit-user-contact').value = userData.data.phone;
                if (document.getElementById('edit-username')) {
                    document.getElementById('edit-username').value = userData.data.username || '';
                }
                document.getElementById('editUserForm').action = `/users/update-user/${userId}/`;


                // Fetch member ledger to display account checkboxes
                fetch('/accounts/fetch-member-ledger/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        MembNum: userData.data.member_id
                    })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(apiData => {
                        console.log('API Data:', apiData);

                        if (apiData.isSuccess) {
                            const ledgerData = apiData.result;
                            console.log('Ledger data:', apiData.result);
                            showAccountCheckbox(ledgerData, userData.data.available_accounts);
                        } else {
                            document.getElementById('account-list-edit').innerHTML =
                                `<div class="alert alert-danger" role="alert">${apiData.error}</div>`;
                        }
                    })
                    .catch(error => {
                        showBaseModal(false);
                        console.error('Error fetching external accounts:', error);
                        document.getElementById('account-list-edit').innerHTML =
                            `<div class="alert alert-danger" role="alert">
                    Failed to retrieve data from external API
                </div>`;
                    });

                // Show the offcanvas
                const offcanvasElement = document.getElementById('offcanvasEditUser');
                const offcanvas = new bootstrap.Offcanvas(offcanvasElement);
                offcanvas.show();
            } else {
                showBaseModal(false);
                alert('Failed to fetch user data: ' + userData.message);
            }
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            alert('Error fetching user data: ' + error);
            showBaseModal(false);
        });
}

function showAccountCheckbox(ledgerData, userAccounts) {
    const accountList = document.getElementById('account-list-edit');
    accountList.innerHTML = '';
    ledgerData.forEach(account => {
        const isChecked = userAccounts.includes(account.AccNum);
        const accountItem = document.createElement('div');
        accountItem.classList.add('mb-3', 'p-2', 'border', 'rounded'); // Add Bootstrap margin, padding, border, and rounded corner classes

        // Create the label and checkbox input with Bootstrap styling
        accountItem.innerHTML = `
            <div class="form-check">
                <input type="checkbox" class="form-check-input" ${isChecked ? 'checked' : ''} id="account-${account.AccountNo}" name="accounts" value="${account.AccNum}">
                <label class="form-check-label" for="account-${account.AccountNo}">
                    ${account.GroupName} - ${account.AccNum} 
                </label>
            </div>`;
        accountList.appendChild(accountItem);
    });
}







////// handle errrors

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addNewUserForm");

    form.addEventListener("submit", function (event) {
        event.preventDefault();  // Prevent the default form submission
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()  // Ensure CSRF token is included if needed
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    // Handle success: show message, redirect, or update UI
                    alert(data.message);
                    window.location.reload();  // Or redirect as needed
                } else if (data.status === "error") {
                    // Handle errors: display them on the form
                    displayFormErrors(data.errors);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An unexpected error occurred. Please try again.');
            });
    });

    function displayFormErrors(errors) {
        // Clear previous errors
        document.querySelectorAll(".error-message").forEach(e => e.remove());

        // Display new errors
        Object.keys(errors).forEach(field => {
            const inputElement = document.getElementById(`add-user-${field}`);
            const errorMessage = document.createElement("div");
            errorMessage.classList.add("error-message");
            errorMessage.textContent = errors[field];
            inputElement.parentNode.appendChild(errorMessage);
        });
    }
});

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
