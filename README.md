# ONR-ISR

This project is a 2D ISR simulator used in several of our recent works. In our studies, we used the simulator to control agents in Microsoft Flight Simulator to represent an ISR scenario off the coast of San Diego.

The simulator was designed in conjunction with US Air Force and US Navy personnel to mimic standard procedures and flight paths. The project is intended for in-person user studies. We plan to remake the simulator in PyGame for use in reinforcement learning projects.

## Running the simulator

The simulator is built in HTML/JS and uses Python Flask to control the state. To start the simulator webserver:

`python webserver.py`

The server will start a webserver that a browser can connect to. The webserver will also try to establish a connection to Microsoft Flight Simulator to mirror agents in MSFS from the agents in the simulator.

To access the experimenter's control panel, open a web browser and navigate to:

`http://localhost:100/control`

This page allows the experimentor to reset the experiment and set various settings for the quantity of ships and game level (all friendly, take damage, etc).

To access the user view, open a web browser and navigate to:

`http://localhost:100`

This page is the user's simulator page where they interact with an complete the study. Importantly, computation for the simulation itself is done on the user's simulator page, NOT the webserver. This was done to remove latency from the simulation and the user's view, for a more streamlined user experience. We intend to change this in our future PyGame port of the simulator.

By default, many aspects of the waypoint navigation and gameplay can be controlled from the user. This is done for demonstration and testing. You can include the following URL parameters, which will prevent the user from changing these aspects or set the study to "user study" mode (no control):

```
live=(true, false)
userId=(string)
gameplayColor=(white, yellow, red)
targetsIteration=(A, B, C, D, E)
motionIteration=(F, G, H, I, J, K)
searchPattern=(ladder, hold, square)
AILevel=(Level0, Level1, Level2, Level3)
```

For example:

`http://localhost:100?userId=12321&gameplayColor=yellow&targetsIteration=D&motionIteration=J&searchPattern=hold&AILevel=Level2`
 
For a user study you can add `live=true` which will disable the parameters box:

`http://localhost:100?userId=12321&gameplayColor=yellow&targetsIteration=D&motionIteration=J&searchPattern=hold&&AILevel=Level2&live=true`

## Parameters

Details of the high-level configuration parameters (URL arguments) follow:

`live` : `true` removes the configuration panel from the user; `false` or not provided allows the user to set the simulator configuration
`userId` : the string in which logs are saved under
`gameplayColor` : `white` gives the user full access to the map; `yellow` declares the right 20% of the map a yellow "no go" zone; `red` declares the right 20% of the map a red "no go" zone; this is visual-only
`targetsIteration` : the number of targets, `A` has 10 targets, `B` has 20 targets, `C` has 30 targets, `D` has 50 targets, `E` has 100 targets
`motionIteration` : the speed of targets, `F` moves targets at 0 units/sec; `G` moves targets at 5 units/sec; `H` moves targets at 10 units/sec; `I` moves targets at 15 units/sec; `J` randomly assigns targets to the other speeds, weighted towards slow speeds; `K` randomly assigns targets to the other speeds, weighted towards high speeds
`searchPattern` : the aircraft's default pattern, `ladder` is an "up and across" pattern; `hold` is a holding pattern (the user must set all waypoints); `square` is a box pattern
`AILevel` : the aircraft flight behavior, `Level0` just follows waypoints; `Level1` randomly rejects user waypoints; `Level2` uses A* to avoid obstacles in the path; `Level3` randomly suggests an alternative search pattern 

Various low-level configuration parameters (aircraft scale, ship scale, visibility of simulator info, grid size for A*) can be set in `templates/index.html`. The base aircraft and ship speeds can be set in `static/js/objects/TargetShip.js` and `static/js/objects/UserAircraft.js`.

## Any issues?

If you have any problems setting up or running the simulator, please open an issue on this project and we will help you out!
