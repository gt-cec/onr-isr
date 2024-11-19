class UserAircraft {
    constructor(startX, startY, path) {
        this.x = startX;
        this.y = startY;
        this.path = path;

        this.originalPath = new WaypointPath(path.waypoints)
        this.optimizedPath = new WaypointPath([]);
        this.nextWaypoint = new Waypoint(this.path.currentWaypoint.x, this.path.currentWaypoint.y, this);
        this.collAvoidWaypoint = new Waypoint(this.path.currentWaypoint.x, this.path.currentWaypoint.y, this);

        this.speed = 5;
        this.rotation = 0;
        this.runningDistanceFromWaypoint = 999;

        this.simx = 0.5;
        this.simy = 0.5;
        this.simheading = 0;
    }

    draw(ctx, Astarpath) {
        ctx.save();

        // if Vector exists, update nextWaypoint
        if (userAircraftVector){
            this.nextWaypoint.x = clickX;
            this.nextWaypoint.y = clickY;

            // Draw the waypoint location
            ctx.beginPath()
            ctx.setLineDash([5, 10]);
            ctx.fillStyle = "black"
            //console.log(userAircraftScale)
            ctx.ellipse(this.nextWaypoint.x, this.nextWaypoint.y, toPx(0.01)*userAircraftScale, toPx(0.01)*userAircraftScale, 0, 0, 2*Math.PI)
            ctx.fill()
    
            // Draw a dashed line to the nextWaypoint
            ctx.beginPath()
            ctx.strokeStyle = "black"
            ctx.moveTo(this.x, this.y)
            ctx.lineTo(this.nextWaypoint.x, this.nextWaypoint.y)
            
            ctx.stroke()
        }
        

         // Draw the Aircraft nextWaypoint if parameterized to
        if (showAircraftWaypoint) {
            // Draw the waypoint location
            ctx.beginPath()
            ctx.setLineDash([]);
            ctx.fillStyle = "black"
            //console.log(this.path.currentWaypoint.x)
            ctx.ellipse(this.path.currentWaypoint.x, this.path.currentWaypoint.y, toPx(0.01)*userAircraftScale, toPx(0.01)*userAircraftScale, 0, 0, 2*Math.PI)
            ctx.fill()
    
            // Draw a solid line to the nextWaypoint
            ctx.beginPath()
            ctx.strokeStyle = "black"
            ctx.moveTo(this.x, this.y)
            ctx.lineTo(this.path.currentWaypoint.x, this.path.currentWaypoint.y)
            ctx.stroke()    
        }

        if (showCollAvoidWaypoints){

            // plot the Astarpath
            Astarpath.forEach((node) => {
                // Draw the waypoint location
                ctx.beginPath()
                ctx.fillStyle = "green"
                let xy = gridToPx(node.y,node.x)
                ctx.ellipse(xy.x, xy.y, toPx(0.01)*.4, toPx(0.01)*.4, 0, 0, 2*Math.PI)
                ctx.fill()
            });
        }

        // Draw the aircraft Search Pattern
        if (showSearchPattern){
            this.path.waypoints.forEach((point) => {
                ctx.beginPath();
                ctx.strokeStyle = "black";
                ctx.rect(point.x - toPx(0.02)*userAircraftScale, point.y - toPx(0.02)*userAircraftScale, toPx(0.04)*userAircraftScale, toPx(0.04)*userAircraftScale);
                ctx.stroke();
            });
        }

        if(showOptimizedSearchPattern){
            this.optimizedPath.waypoints.forEach((point) => {
                ctx.beginPath();
                ctx.strokeStyle = "red";
                ctx.rect(point.x - toPx(0.02)*userAircraftScale, point.y - toPx(0.02)*userAircraftScale, toPx(0.04)*userAircraftScale, toPx(0.04)*userAircraftScale);
                ctx.stroke();
            });
        }

        // move and rotate aircraft towards next waypoint
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);
    
        /* User Aircraft */
        ctx.fillStyle = "orange";
    
        // Wings
        let wingWidth = toPx(0.1)*userAircraftScale;
        let wingHeight = toPx(0.0125)*userAircraftScale;
        ctx.beginPath();
        ctx.fillRect(0 - wingWidth/2, 0 - wingHeight/2, wingWidth, wingHeight);
    
        // Body
        let bodyWidth = toPx(0.0125)*userAircraftScale;
        let bodyHeight = toPx(0.1)*userAircraftScale;
        ctx.beginPath();
        ctx.fillRect(0 - bodyWidth/2, 0 - bodyHeight*(1/3), bodyWidth, bodyHeight);
    
        // Tail
        let tailWidth = wingWidth/3;
        let tailHeight = wingHeight;
        ctx.beginPath();
        ctx.fillRect(0 - tailWidth/2, (0 + bodyHeight*(2/3)) - tailHeight/2, tailWidth, tailHeight);
    
        /* Visuals */
        ctx.strokeStyle = "orange";
    
        // Visual Radius
        let visualRadius = gameWidth*(0.3/2); // Slide 23 says r=30 but visually appears to be r=15
        ctx.beginPath();
        ctx.ellipse(0, 0, visualRadius, visualRadius, 0, 0, 2*Math.PI);
        ctx.setLineDash([]);
        ctx.stroke();
    
        // ISAR Radius
        let isarRadius = gameWidth*(0.5/2);
        ctx.beginPath();
        ctx.ellipse(0, 0, isarRadius, isarRadius, 0, Math.PI, 2*Math.PI);
        ctx.moveTo(0 - isarRadius, 0);
        ctx.lineTo(0 + isarRadius, 0);
        ctx.setLineDash([5, 10]);
        ctx.stroke();
        ctx.restore();

    }
    move() {
        this.rotation = this.path.getDirection(this.x, this.y);
        let dx = NmToPx(this.speed) * Math.cos(this.rotation - Math.PI / 2) * simPeriod / 1000
        let dy = NmToPx(this.speed) * Math.sin(this.rotation - Math.PI / 2) * simPeriod / 1000;
        this.x += dx;
        this.y += dy

        if (useMSFScoords){
            this.x =  this.simx* gameWidth + zeroX
            this.y = this.simy* gameHeight + zeroY
            //mag variation in San Diego 11.5 degree East; add 11.5 degree to mag heading to find true heading
            //+ (11.5) * Math.PI/180
            let theta = this.simheading 
            if (theta < 0) { theta += 2*Math.PI; }
            theta %= 2*Math.PI;
            this.rotation = this.simheading
            //console.log("simx=", this.x, " simy=", this.y, " simheading=", this.rotation*180/Math.PI)
        }
        
    }
    getRangeType(target) {
        // Distance
        let distanceToTarget = distance(this.x, target.x, this.y, target.y);
        
        // Angle
        let theta = Math.atan2((target.y - this.y), (target.x - this.x));
        theta -= this.rotation;
        while (theta < 0) { theta += 2*Math.PI; }
        theta %= 2*Math.PI;

        // Calculate type
        if (distanceToTarget <= gameWidth*(0.3/2)) {
            return 2; // visual
        } else if (distanceToTarget <= gameWidth*(0.5/2) && theta > Math.PI && theta < 2*Math.PI) {
            return 1; // isar
        } else {
            return 0; // none
        }
    }
    optimize(shift_east, shift_south ){  
        this.optimizedPath = new WaypointPath([]);
        this.originalPath.waypoints.forEach(point => {
            let xi = (point.x)/2 + shift_east + 0.1 * gameWidth
            let yi = (point.y)/2 + shift_south + 0.1 * gameHeight
            this.optimizedPath.waypoints.push(new Waypoint(xi, yi,this.optimizedPath) )
        });
    }
}
