
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

document.getElementById('confirmActionButton').addEventListener('click', function () {
    showBaseModal(true);
    actionData['csrfmiddlewaretoken'] = getCsrfToken();
    $.ajax({
        type: 'POST',
        url: actionUrl,
        data: actionData,
        success: function (response) {
            alert(response.message);
            showBaseModal(false);
            location.reload();  // Reload the page to reflect changes
        },
        error: function (response) {
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

function deleteUser(userId) {
    const deleteUserUrl = '/users/delete-user/'; // Static URL
    showModal(
        deleteUserUrl,
        {
            'user_id': userId
        },
        'Are you sure you want to delete this user?'
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


// Fetch data from thirdparty backend
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-member');
    const suggestionsBox = document.createElement('div');
    suggestionsBox.classList.add('suggestions-box');
    if (searchInput) {
        searchInput.parentNode.appendChild(suggestionsBox);
    }

    let members = [];

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const searchText = this.value;
            // Fetch member data from the server
            fetch('/accounts/member-search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ SearchText: searchText })
            })
                .then(response => response.json())
                .then(data => {

                    if (data.isSuccess) {
                        members = JSON.parse(data.result);  // Parse the JSON string
                        filterSuggestions(searchText);
                    } else {
                        console.error('Failed to fetch members:', data);
                    }

                })
                .catch(error => {
                    console.error('Error fetching members:', error);
                });
        });
    }

    function filterSuggestions(searchText) {
        const filtered = members.filter(member =>
            member.MemberName.toLowerCase().includes(searchText.toLowerCase()) ||
            member.MemberNum.toLowerCase().includes(searchText.toLowerCase()) ||
            (member.Mobile && member.Mobile.toLowerCase().includes(searchText.toLowerCase())) ||
            (member.PostalAddress && member.PostalAddress.toLowerCase().includes(searchText.toLowerCase()))
        );
        displaySuggestions(filtered);
    }

    function displaySuggestions(filtered) {
        suggestionsBox.innerHTML = '';

        filtered.forEach(member => {
            const suggestionItem = document.createElement('div');
            suggestionItem.classList.add('suggestion-item');
            suggestionItem.textContent = `${member.MemberName} (${member.MemberNum})`;
            suggestionItem.addEventListener('click', function () {
                fetchMemberLedger(member);
                suggestionsBox.innerHTML = '';  // Clear suggestions
            });
            suggestionsBox.appendChild(suggestionItem);
        });

        if (filtered.length === 0) {
            const noResultsItem = document.createElement('div');
            noResultsItem.classList.add('suggestion-item');
            noResultsItem.textContent = 'No results found';
            suggestionsBox.appendChild(noResultsItem);
        }
    }


    function fetchMemberLedger(member) {
        showBaseModal(true);
        fetch('/accounts/member-ledger/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                MembNum: member.MemberNum,
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.isSuccess) {
                    const ledgerData = JSON.parse(data.result);
                    console.log('Fetched accounts:', ledgerData);
                    fillFormWithMemberData(member);
                    displayAccountList(ledgerData);
                } else {
                    console.error('Failed to fetch member ledger:', data);
                }
                showBaseModal(false);
            })
            .catch(error => {
                console.error('Error fetching member ledger:', error);
                showBaseModal(false);
            });
    }

    function fillFormWithMemberData(member) {
        document.getElementById('add-user-firstname').value = member.MemberName.split(' ')[0];
        document.getElementById('add-user-lastname').value = member.MemberName.split(' ').slice(1).join(' ');
        document.getElementById('add-user-email').value = member.Email || '';
        document.getElementById('add-user-contact').value = member.Mobile || '';
        document.getElementById('add-user-member-number').value = member.MemberNum || '';
    }

    function displayAccountList(ledgerData) {
        const accountList = document.getElementById('account-list');
        accountList.innerHTML = '';

        ledgerData.forEach(account => {
            const accountItem = document.createElement('div');
            accountItem.classList.add('account-item');
            accountItem.innerHTML = `
                <input type="checkbox"  id="account-${account.AccountNo}" name="accounts" value="${account.AccNum}">
                <label for="account-${account.AccountNo}">
                    ${account.GroupName} (${account.AccNum}): ${account.PBal}
                </label>
            `;
            accountList.appendChild(accountItem);
        });
    }


    // Fetch and display accounts when the form is opened for branch/member roles
    const offcanvasAddUser = document.getElementById('offcanvasAddUser');
    offcanvasAddUser.addEventListener('shown.bs.offcanvas', function () {
        if (!searchInput) {
            fetchAccountDetails();
        }
    });

    function fetchAccountDetails() {
        showBaseModal(true);
        fetch('/accounts/fetch-member-ledger/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({

                MembNum: member.MemberNum
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.isSuccess) {
                    const ledgerData = JSON.parse(data.result);
                    displayAccountList(ledgerData);
                } else {
                    console.error('Failed to fetch accounts:', data);
                }
                showBaseModal(false);
            })
            .catch(error => {
                console.error('Error fetching accounts:', error);
                showBaseModal(false);
            });

        showBaseModal(false);
    }
});


//// User Edit Offcanvas


function showUserEditCanvas(userId) {
    fetch(`/users/get_user_info/${userId}/`)
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


                // Fetch external accounts


                console.log('Fetching external accounts...');
                console.log(userData.data);
                showBaseModal(true);
                fetch('/accounts/fetch-member-ledger/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        MembNum: userData.data.member_number
                    })
                })
                    .then(response => response.json())
                    .then(apiData => {
                        showBaseModal(false);
                        if (apiData.isSuccess) {
                            // Show available accounts checkboxes
                            const userAccounts = userData.data.available_accounts;


                            const ledgerData = JSON.parse(apiData.result);

                            showAccountCheckbox(ledgerData, userAccounts);
                        } else {
                            document.getElementById('account-list-edit').innerHTML = `
                            <div class="alert alert-danger" role="alert">
                                ${apiData.error}
                            </div>`;
                        }
                    })
                    .catch(error => {
                        showBaseModal(false);
                        console.error('Error fetching external accounts:', error);
                        document.getElementById('account-list-edit').innerHTML = `
                        <div class="alert alert-danger" role="alert">
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
            showBaseModal(true);
        });
}

function showAccountCheckbox(ledgerData, userAccounts) {
    const accountList = document.getElementById('account-list-edit');
    accountList.innerHTML = '';
    ledgerData.forEach(account => {
        const isChecked = userAccounts.includes(account.AccNum);
        const accountItem = document.createElement('div');
        accountItem.classList.add('account-item');
        accountItem.innerHTML = `
            <input type="checkbox" ${isChecked ? 'checked' : ''} id="account-${account.AccountNo}" name="accounts" value="${account.AccNum}">
            <label for="account-${account.AccountNo}">
                    ${account.GroupName} (${account.AccNum}): ${account.PBal}
                </label>
        `;
        accountList.appendChild(accountItem);
    });
}








