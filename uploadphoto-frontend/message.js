document.addEventListener('DOMContentLoaded', function() {
    const selectedChoiceText = document.getElementById('selected-choice');

    // Get the selected choice from localStorage
    const selectedChoice = localStorage.getItem('selectedChoice');

    // Display the chosen option
    if (selectedChoice) {
        selectedChoiceText.textContent = `You selected: ${selectedChoice}`;
    } else {
        selectedChoiceText.textContent = "No choice selected.";
    }

    const form = document.getElementById('proof-img');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevents form submission

        // Pops up the message
        alert(`Thank you for your submission! We will review it soon.`);

        // Reset the form
        form.reset();

        // Reload the page
        location.reload();
    });
});
