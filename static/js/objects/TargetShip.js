class TargetShip {
    constructor(startX, startY, speed, id, targetClass, threatClass) {
        // Motion
        this.x = startX
        this.y = startY
        this.speed = speed
        this.dirTheta = -1
        this.runningDistanceFromWaypoint = Infinity  // distance from the waypoint, used to test if the object has overshot

        this.closestApproachDistance = Infinity // Closest Approach Distance of Aircraft

        this.waypointCount = 1
        this.waypointArrayX = []
        this.waypointArrayY = []

        // Set first waypoint (spawn point)
        this.waypointArrayX[0] = startX
        this.waypointArrayY[0] = startY

        // Set the rest of the waypoints
        for (let i = 1; i < 30; i++)
            this.setRandomWaypoint()

        this.waypointCount = 1
        this.waypointX = this.waypointArrayX[this.waypointCount]
        this.waypointY = this.waypointArrayY[this.waypointCount]

        // Information
        this.id = id
        this.targetClass = targetClass
        this.threatClass = threatClass
        this.seenTargetClass = false;
        this.seenThreatClass = false;
        this.mousedOver = false;
        this.currentlyMousedOver = false;
        this.textLines = [];
        this.dangerRadius = 0.0;

        this.numClassification = 0;
        this.prevRangeType = 0;
        
        switch (this.threatClass) {
             case 1: this.dangerRadius = gameWidth*(0.05/2); break
             case 2: this.dangerRadius = gameWidth*(0.1/2); break
             case 3: this.dangerRadius = gameWidth*(0.15/2); break
            }

        // Alerting
        this.isVisible = false      
    }

    renderText(ctx) {
        ctx.font = "normal 600 20px Roboto"
        ctx.fillStyle = "black"

        // render the text
        let xRel = 0.01
        let yRel = this.textLines.length * 0.02
        for (let i=0; i<this.textLines.length; i++) {
            ctx.fillText(this.textLines[i], this.x + toPx(xRel), this.y - toPx(yRel))
            yRel -= 0.02
        }
    }

    draw(ctx, userAircraft) {
        // Get the range
        let rangeType = userAircraft.getRangeType(this)

        // Default information
        this.textLines = [
            `Track ID ${this.id}`,
            "Position:",
            `    (${Math.round((this.x - gameWidth/2) * 1) / 1}, ${Math.round((-(this.y - gameHeight/2)) * 1) / 1})`,
        ]
        // add conditional lines to the mouseover info
        if (rangeType === 1 || rangeType === 2 || this.seenTargetClass) {
            //this.textLines.push(`Speed: ${this.speed} knts`)
            //this.textLines.push(`Target Class: ${this.targetClass}`)
            //this.textLines.push(`Tracking: ${this.numClassification}x`)
            
            if (rangeType == 1 && !this.seenThreatClass) {
                this.textLines.push(`Threat Class: UKN`)
                this.seenTargetClass = true
            }
            else if (rangeType == 2) {
                this.textLines.push(`Threat Class: ${this.threatClass}`)
                this.seenThreatClass = true
            }
        }

        // Set the appropriate color
        if (this.seenTargetClass == false) {
            ctx.fillStyle = "gold"
        } else {
            if (this.targetClass === 0) {
                ctx.fillStyle = "purple"
            } else {
                ctx.fillStyle = "red"
            }
        }

        // Draw the circle
        ctx.beginPath()
        ctx.ellipse(this.x, this.y, toPx(0.02)*targetShipScale, toPx(0.02)*targetShipScale, 0, 0, 2*Math.PI)
        ctx.fill()

        // Draw the waypoint if parameterized to
        if (showTargetShipWaypoints) {
            // Draw the waypoint location
            ctx.beginPath()
            ctx.fillStyle = "black"
            ctx.ellipse(this.waypointX, this.waypointY, toPx(0.005)*targetShipScale, toPx(0.005)*targetShipScale, 0, 0, 2*Math.PI)
            ctx.fill()
    
            // Draw a line to the ship
            ctx.beginPath()
            ctx.strokeStyle = "black"
            ctx.moveTo(this.x, this.y)
            ctx.lineTo(this.waypointX, this.waypointY)
            ctx.stroke()    
        }

        // Display Text
        let distanceToMouse = distance(this.x, mouseX, this.y, mouseY)
        if (distanceToMouse <= toPx(0.02)*targetShipScale) {
            this.mousedOver = true;
            this.currentlyMousedOver = true;
        } 
        else {
            this.currentlyMousedOver = false;
        }

        if (rangeType === 1) {
            this.seenTargetClass = true;
            // for non enemy ships, also make target and threat detection range the same
            if (this.targetClass=== 0){
                this.seenThreatClass = true;
            }
        }

        if (rangeType === 2) {
            this.seenTargetClass = true;
            this.seenThreatClass = true;
        }

        // Display danger ring for combatants that have been classified
        if (this.seenThreatClass) {
           
            ctx.beginPath()
            ctx.strokeStyle = "red"
            ctx.ellipse(this.x, this.y, this.dangerRadius, this.dangerRadius, 0, 0, 2*Math.PI)
            ctx.setLineDash([])
            ctx.stroke()
        }
        
        // increment number of times classified at transition from radar to visual
        if (rangeType == 2 && this.prevRangeType== 1 ){
            this.numClassification++
        }
        // save previous rangeType
        this.prevRangeType = rangeType  
    }

    move() {
        // if close to target waypoint and we aren't moving targets offscreen, generate a new waypoint
        let dist = distance(this.x, this.waypointX, this.y, this.waypointY)
        if (!moveTargetsOffscreen && dist > this.runningDistanceFromWaypoint) {
            this.waypointCount++
            this.waypointX = this.waypointArrayX[this.waypointCount]
            this.waypointY = this.waypointArrayY[this.waypointCount]
            this.runningDistanceFromWaypoint = Infinity
            return
        }
        else {
            this.runningDistanceFromWaypoint = dist
        }

        // get the direction of the target ship if we aren't moving targets offscreen
        if (!moveTargetsOffscreen || this.dirTheta == -1 || this.dirTheta == NaN) {
            this.dirTheta = Math.atan2(this.waypointY - this.y, this.waypointX - this.x)
        }

        // move the target ship        
        this.x += NmToPx(this.speed / 10) * Math.cos(this.dirTheta) * simPeriod / 1000
        this.y += NmToPx(this.speed / 10) * Math.sin(this.dirTheta) * simPeriod / 1000
    }

    setRandomWaypoint() {
        this.runningDistanceFromWaypoint = Infinity
        this.waypointArrayX[this.waypointCount] = zeroX + rand() * gameWidth
        this.waypointArrayY[this.waypointCount] = zeroY + rand() * gameHeight
        this.waypointCount++
    }
}
