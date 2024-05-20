
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
        let waypointX = this.currentWaypoint.x;
        let waypointY = this.currentWaypoint.y;
        
        if (userAircraftVector){
            // if userAircraftVector, override AI search pattern
            //waypointX = newX;
            //waypointY = newY;
            waypointX = clickX;
            waypointY = clickY;
            // if new userAircraftVector, then move next AI waypoint to next waypoint in search pattern
            if ((prevUserAircraftVector == false) || ((newX != clickX))){
                //console.log("new userAircraftVector")
                // this.currentWaypointIndex++;
                // if (this.currentWaypointIndex === this.waypoints.length) {
                //     this.currentWaypointIndex = 0;
                // }
                // send new destination waypoint to webserver
                if (useMSFScoords){
                    fetch('/current-destination', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({"dest x": (waypointX - zeroX) / gameWidth, "dest y": (waypointY - zeroY) / gameWidth})
                    }).catch((error) => {
                        //console.error('Error:', error);
                        console.log("Failed to send sim current destination!!")   
                    });
                }
                
            }
            this.currentWaypoint = this.waypoints[this.currentWaypointIndex]; 
        }
        // Check if the object has arrived at the current waypoint target
        // 
        let distance = Math.sqrt(Math.pow(Math.abs(waypointX - x), 2) + Math.pow(Math.abs(waypointY - y), 2));
        if (distance <= toPx(this.arrivalRadius)) {
            
            // // Start the next waypoint target, increment if AI waypoint, otherwise already done
            // if(!userAircraftVector){
            //     this.currentWaypointIndex++;
            //     // if at end of waypoint list, reset
            //     if (this.currentWaypointIndex === this.waypoints.length) {
            //         this.timesCompleted++;
            //         this.currentWaypointIndex = 0;
            //     }
            //     this.currentWaypoint = this.waypoints[this.currentWaypointIndex];  
            // }

            // Start the next waypoint target, increment if AI waypoint
            if (newX != waypointX) this.currentWaypointIndex++;
                // if at end of waypoint list, reset
                if (this.currentWaypointIndex === this.waypoints.length) {
                    this.timesCompleted++;
                    this.currentWaypointIndex = 0;
                }
                this.currentWaypoint = this.waypoints[this.currentWaypointIndex]; 
            // send new destination waypoint to webserver
            if (useMSFScoords){
                fetch('/current-destination', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"dest x": (this.currentWaypoint.x - zeroX) / gameWidth, "dest y": (this.currentWaypoint.y - zeroY) /gameWidth})
                }).catch((error) => {
                //console.error('Error:', error);
                    console.log("Failed to send sim current destination!!")   
                });
            }
            
            // clear the User Vector 
            userAircraftVector = false;
        }
        // update previous userAircraftVector
        prevUserAircraftVector = userAircraftVector;
        // Get the angle
        let theta = Math.atan2((waypointY - y), (waypointX - x));
        if (theta < 0) { theta += 2*Math.PI; }
        theta += Math.PI / 2; // Canvas rotation starts 0deg as up
        theta %= 2*Math.PI;
        return theta;
    }
}