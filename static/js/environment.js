// utility function to convert a percentage value to a pixel value for drawing, e.g., 0.8 is 80% of the canvas gameHeight/gameWidth
function toPx(val) {
    return val * canvasLength
}

// utility function to convert a nautical mile value to a pixel value for speed conversions
function NmToPx(val) {
    return val * canvasLength / 100  // the 150 here is just an arbitrary value which we will scale
}

// Utility function to get the position of a percentage of the surveillance area
function toSurv(percentX, percentY) {
    return {
        "x": zeroX + gameWidth*0.1 + gameWidth*0.8*percentX,
        "y": zeroY + gameHeight*0.1 + gameHeight*0.8*percentY,
    }
}

// utility function to get the percentage of the surveillance area of a pixel position
function toSurvPct(pixelX, pixelY){
    return{
        "x": (pixelX - zeroX) / (gameWidth),
        "y": (pixelY - zeroY) / (gameHeight)
    }
}

// utility function to get the 2D grid coordinates of a pixel 
function pxToGrid(pixelX, pixelY){
    return{
        "x": Math.max(0, Math.min(Math.floor(((pixelX-zeroX-gridWidth/2)/gameWidth)*gridWidth), gridWidth-1)),
        "y": Math.max(0,Math.min(Math.floor(((pixelY-zeroY-gridHeight/2)/gameHeight)*gridHeight), gridHeight-1))
    }
}

// utility function to turn 2D grid coordinates to pixel coords
function gridToPx(gridX, gridY){
    // if only the grid indices are used, the points will be at the top left, so instead make the points at the middle
    return{
        "x":zeroX + (gridX/gridWidth)*gameWidth + gridWidth/2,
        "y":zeroY + (gridY/gridHeight)*gameHeight + gridHeight/2
    }
}

function distance(x1, x2, y1, y2) {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

// draw the environment lines
function drawEnvironment(ctx) {

    // Set solid line
    ctx.setLineDash([]);

    // Artificial Boundary
    ctx.strokeStyle = "black";
    ctx.beginPath();
    ctx.rect(zeroX, zeroY, gameWidth, gameHeight);
    ctx.stroke();

    // Surveillance Area 
    ctx.strokeStyle = "green";
    ctx.beginPath();
    ctx.rect(zeroX + gameWidth*0.1, zeroY + gameHeight*0.1, gameWidth*0.8, gameHeight*0.8);
    ctx.stroke();

    // Line Divisions
    ctx.strokeStyle = "black";
    ctx.beginPath();
    ctx.moveTo(zeroX + gameWidth*0.5, zeroY);
    ctx.lineTo(zeroX + gameWidth*0.5, zeroY + gameHeight);
    ctx.moveTo(zeroX, zeroY + gameHeight*0.5);
    ctx.lineTo(zeroX + gameWidth, zeroY + gameHeight*0.5);
    ctx.stroke();

    // No-go zone
    if (gameplayColor === "yellow" || gameplayColor === "red") {

        switch (gameplayColor) {
            case "red": ctx.fillStyle = "rgba(255, 0, 0, 0.5)"; break;
            case "yellow": ctx.fillStyle = "rgba(200, 150, 0, 0.5)"; break;
        }

        ctx.beginPath();
        ctx.fillRect(zeroX + gameWidth*0.8, zeroY, gameWidth*0.2, gameHeight);
        ctx.stroke();
    }

}

