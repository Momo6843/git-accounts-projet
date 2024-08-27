document.addEventListener("DOMContentLoaded", function () {
    const profileSelect = document.querySelector("#id_profile");
    const accountTypesContainer = document.querySelector("#id_account_types");

    if (profileSelect && accountTypesContainer) {
        profileSelect.addEventListener("change", function () {
            const profileId = profileSelect.value;

            if (profileId) {
                fetch(`/accounts/get_account_types/?profile_id=${profileId}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        const checkboxes = accountTypesContainer.querySelectorAll("input[type='checkbox']");
                        checkboxes.forEach(checkbox => {
                            checkbox.checked = data.account_types.includes(parseInt(checkbox.value));
                        });
                    })
                    .catch(error => {
                        console.error('There has been a problem with your fetch operation:', error);
                    });
            }
        });
    }
});
