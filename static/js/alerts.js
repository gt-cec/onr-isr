function pushAlert(message, emergency=false) {
    // Create new alert
    let alerts = document.getElementById("main-alerts");
    let newAlert = document.createElement("li");
    let alertData = [];
    if (emergency) {
        newAlert.style.color = "red"
        newAlert.textContent = "• " + message;
        // set up a flash
        alertOverlay() 
    }
    else {
        newAlert.textContent = "• " + message;
    }
    alerts.appendChild(newAlert);
    
    alertData.push({message});
    fetch('/receive-alert', {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json'
        },
        body: JSON.stringify(alertData)
    }).then(response => {
                return response.json();
    }).then(data => {
    //console.log(data);
    }).catch(error => {
        if (error.message.includes('JSON.parse: unexpected character at line 1 column 1 of the JSON data')) { return; }
        else console.error('Error:', error);
    });
    alertData = []

    return newAlert;
}

function alertOverlay() {
    var count = 0;
    var intervalId = setInterval(function() {
        if (document.getElementById("emergency-alert").style.display == "none") {
            document.getElementById("emergency-alert").style.display = "flex"
            // increment counter when showing to count # of blinks and stop when visible
            if (count++ === 2) {
                document.getElementById("emergency-alert").style.display = "none"
                clearInterval(intervalId);
            }
        } else {
            document.getElementById("emergency-alert").style.display = "none"
        }    
    }, 400);
}

function emptyAlert() {
    alerts.appendChild(document.createElement("br"));
}

function removeAlert(alert) {
    let alerts = document.getElementById("main-alerts");
    alerts.removeChild(alert);
}
