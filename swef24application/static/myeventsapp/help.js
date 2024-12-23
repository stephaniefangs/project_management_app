/*
Sources:
- HTML DOM Element classList - https://www.w3schools.com/jsreF/prop_element_classlist.asp
*/

function toggleHelp() {
    const popup = document.getElementById('helpPopup');
    popup.classList.toggle('show');
}

// Close popup when clicking outside
document.addEventListener('click', function(event) {
    const popup = document.getElementById('helpPopup');
    const helpButton = document.querySelector('.help-button');
    
    if (!popup.contains(event.target) && event.target !== helpButton) {
        popup.classList.remove('show');
    }
});