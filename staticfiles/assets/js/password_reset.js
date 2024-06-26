document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('passwordChangeForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                const errorDiv = document.getElementById('formErrors');
                errorDiv.innerHTML = '';
                for (const [key, value] of Object.entries(data.errors)) {
                    errorDiv.innerHTML += `${value}<br>`;
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});