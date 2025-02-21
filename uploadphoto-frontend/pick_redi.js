document.addEventListener('DOMContentLoaded', function() {
    const showChoicesButton = document.getElementById('show-choices');
    const choicesList = document.getElementById('choices-list');

    // Show the list when the button is clicked
    showChoicesButton.addEventListener('click', function() {
        choicesList.classList.toggle('hidden');
    });

    // Handle choice selection
    document.querySelectorAll('.choice').forEach(button => {
        button.addEventListener('click', function() {
            const selectedChoice = this.getAttribute('data-choice');

            // Store the selected choice in localStorage
            localStorage.setItem('selectedChoice', selectedChoice);

            // Redirect to the upload page
            window.location.href = "upload.html";
        });
    });
});
