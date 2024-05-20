# ONR-ISR
CEC ONR-ISR Project

ISR Simulator.

## Running the simulator

Open `/templates/index.html` in a web browser.

You can include the following URL parameters, which will prevent the user from changing them:

```
userId=(string)
gameplayColor=(white, yellow, red)
targetsIteration=(A, B, C, D, E)
motionIteration=(F, G, H, I, J, K)
searchPattern=(ladder, hold, square)
```

For example:

`.../index.html?userId=12321&gameplayColor=yellow&targetsIteration=D&motionIteration=J&searchPattern=hold`

 
You can add `live=true` which will disable the parameters box

`.../index.html?userId=12321&gameplayColor=yellow&targetsIteration=D&motionIteration=J&searchPattern=hold&live=true`