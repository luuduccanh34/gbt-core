document.addEventListener("DOMContentLoaded", function() {
    if (!document.getElementById("donate-icon")) {
        // Create the donate icon
        const donateDiv = document.createElement('div');
        donateDiv.id = 'donate-icon';
        donateDiv.className = 'donate-icon';
        donateDiv.title = 'Donate / Support';
        donateDiv.innerHTML = '💖';

        // Show thank you toast on click
        donateDiv.onclick = function() {
            var toast = document.getElementById("thank-you-toast");
            if (toast) {
                toast.className = "show";
                setTimeout(function(){
                    toast.className = toast.className.replace("show", "");
                }, 3000);
            }
        };

        document.body.appendChild(donateDiv);

        // Create the toast container
        const toastDiv = document.createElement('div');
        toastDiv.id = 'thank-you-toast';
        toastDiv.innerText = 'Thank you for your interest!';
        document.body.appendChild(toastDiv);
    }
});
