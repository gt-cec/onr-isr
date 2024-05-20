// simple logging function, sends the given data to our webserver
function log(data) {
    data["user-id"] = userId;  // include the user ID
    return fetch("/log", {method: "POST", headers: {
        'Content-Type': 'application/json'
    }, body: JSON.stringify(data)}).catch((error) => {
        //console.error('Error:', error);
        console.log("Failed to log!!")   
      });;
}