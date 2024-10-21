
class Waypoint {
    constructor(x, y, path) {
        this.x = x;
        this.y = y;
        this.path = path;
        this.timesCompleted = 0;
    }
}

class WaypointPath {
    constructor(points) {
        this.waypoints = [];
        points.forEach(point => {
            this.waypoints.push(new Waypoint(point.x, point.y, this));
        });

        this.currentWaypointIndex = 0;
        this.currentWaypoint = this.waypoints[0];
        this.arrivalRadius = 0.01
        if (useMSFScoords){
            this.arrivalRadius = 0.05
        }
    }
    getDirection(x, y) {
        // User Vector override
        //DISTRANCE IS NOT WORKING FOR USER DEFINED WAYPOINTS
        // WAYPOINTX AND WAYPOINTY NEED TO BE INITIALIZED OUTSIDE
        //if (!userAircraftVector && !newClick){
        let waypointX = this.currentWaypoint.x;
        //console.log("Initialization waypointX ", waypointX)
        let waypointY = this.currentWaypoint.y;
        //}

           
        if (userAircraftVector){
            // User Aircraft Vector override of AI Waypoint
            //console.log("detected userAircraftVector")
            waypointX = clickX;
            waypointY = clickY;
            if(newClick){
                console.log("Processed new click X=", waypointX, "Y=", waypointY)
                sendDestinationToMSFS(waypointX, waypointY)
                // // User-defined waypoint
                // let newWaypointX = clickX;
                // let newWaypointY = clickY;
                

                // const epsilon = 0.0001; // Define a small threshold for comparison
                // if (Math.abs(newWaypointX - waypointX) > epsilon || Math.abs(newWaypointY - waypointY) > epsilon) {
                //     waypointX = newWaypointX;
                //     waypointY = newWaypointY;
                //     console.log("new user vector different from current vector")
                //     //let wpX = waypointX
                //     //let wpY = waypointY
                //     sendDestinationToMSFS(waypointX, waypointY)
                // }
                newClick = false;
                // If the previous vector was a user vector (prevUserAircraftVector is true)
                // and the new click is different from the previous waypoint
                // if (prevUserAircraftVector) {
                //     // Check if the new clickX is different from the last waypointX
                //     const epsilon = 0.0001; // Define a small threshold for comparison
                //     if (Math.abs(newWaypointX - waypointX) > epsilon || Math.abs(newWaypointY - waypointY) > epsilon) {
                //         console.log("New user vector, different from the previous one");
                //         // Update waypointX and waypointY to the new user click
                //         waypointX = newWaypointX;
                //         waypointY = newWaypointY;

                //         // Send the new destination to MSFS
                //         sendDestinationToMSFS(waypointX, waypointY);
                //     } 
                //     else {
                //         console.log("New clickX is the same as the previous waypoint, no update needed");
                //     }
                // } 
                //else {
                    // // First user vector after AI or no previous user vector
                    // console.log("User Vector after an AI vector or no previous vector");
                    // waypointX = newWaypointX;
                    // waypointY = newWaypointY;

                    // // Send the new destination to MSFS
                    // sendDestinationToMSFS(waypointX, waypointY);
                //}

                // // if userAircraftVector, override AI search pattern
                // // set user click waypoint as aircraft waypoint
                // //console.log("clickX=", clickX)
                // waypointX = clickX;
                // console.log("waypointX = ClickX =", clickX)
                // waypointY = clickY;
                // // if userAircraftVector aftter an AI vecor
                // if (prevUserAircraftVector == false) {
                //     console.log("User Vector after an AI vector")
                //     // If using MSFS, send destination waypoint to webserver
                //     sendDestinationToMSFS(waypointX, waypointY)
                // }
                // else{}
                // // if user vector after a user vector
                // // and if incoming clickX is different from current 
                // if ((waypointX != clickX)){
                //     console.log("User Vector replacing a User Vector")
                //     // set user click waypoint as aircraft waypoint
                //     waypointX = clickX;
                //     waypointY = clickY;
                //     // If using MSFS, send new destination waypoint to webserver
                //     sendDestinationToMSFS(waypointX, waypointY)
                    
                
                // Update the current waypoint
                //this.currentWaypoint = this.waypoints[this.currentWaypointIndex]; 
            }
        }
        // Check if the object has arrived at the current waypoint target
        //console.log("breakpoint 3 waypointX=", waypointX)
        let distance = Math.sqrt(Math.pow(Math.abs(waypointX - x), 2) + Math.pow(Math.abs(waypointY - y), 2));
        // console.log("distance = ", distance)
        if (distance <= toPx(this.arrivalRadius)) {
            console.log("reached current destination")
            // Start the next waypoint target, 
            // If waypoint reached is not current AI waypoint, next destination is AI waypoint
            if ( waypointX != this.currentWaypoint.x &&  waypointY != this.currentWaypoint.y ) {
                console.log("condition 2")
                waypointX = this.currentWaypoint.x
                waypointY = this.currentWaypoint.y
                
            }
            // If waypint reached is current AI waypoint, increment the index of AI waypoint list
            else{
                //console.log("condition 3")
                this.currentWaypointIndex++;
                // if at end of waypoint list, reset
                if (this.currentWaypointIndex === this.waypoints.length) {
                    this.timesCompleted++;
                    this.currentWaypointIndex = 0;
                }
                this.currentWaypoint = this.waypoints[this.currentWaypointIndex]; 
                waypointX = this.currentWaypoint.x
                waypointY = this.currentWaypoint.y
            }
            
            // if using MSFS, send new destination waypoint from incremented waypoint list to webserver
            let wpX = waypointX
            let wpY = waypointY
            sendDestinationToMSFS(wpX, wpY)
            
            // clear the User Vector 
            userAircraftVector = false;
        }
        // State there exists a prevuserAircraftVector
        prevUserAircraftVector = userAircraftVector;
        // Get the angle
        //console.log("breakpoint 4, waypointX=", waypointX)
        let theta = Math.atan2((waypointY - y), (waypointX - x));
        if (theta < 0) { theta += 2*Math.PI; }
        theta += Math.PI / 2; // Canvas rotation starts 0deg as up
        theta %= 2*Math.PI;
        return theta;
    }

    
}
function sendDestinationToMSFS(waypointX, waypointY) {
    if (useMSFScoords) {
        fetch('/current-destination', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "dest x": (waypointX - zeroX) / gameWidth, "dest y": (waypointY - zeroY) / gameWidth })
        }).catch((error) => {
            console.log("Failed to send sim current destination!!");
        });
    }
}