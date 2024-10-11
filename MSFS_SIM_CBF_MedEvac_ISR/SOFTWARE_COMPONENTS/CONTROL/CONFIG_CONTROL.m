function [CONTROL] = CONFIG_CONTROL(MODEL,SIM_CONTROL_MODE,SCENARIO_CONTROL_MODE,HUMAN_ATT_MODE)
%--------------------------------------------------------------------------
% GENERAL PARAMETERS
%--------------------------------------------------------------------------
% Control sampling time (s)
ts = MODEL.PARAM.SAMPLING_TIME;
CONTROL.PARAM.SAMPLING_TIME = ts;
CONTROL.PARAM.SIM_CONTROL_MODE = SIM_CONTROL_MODE;
%CONTROL.PARAM.TAU_MAX = 20;
CONTROL.PARAM.TAU_MAX = 100;
CONTROL.PARAM.SIM_TIME = 0;
CONTROL.PARAM.FLIGHT_STATUS = 0;
CONTROL.PARAM.TIMER = 0;
CONTROL.PARAM.RESET_POS = 0;
CONTROL.PARAM.TAKE_OFF = 0;
CONTROL.PARAM.LANDING = 0;
%--------------------------------------------------------------------------
% SAFETY FILTERS PARAMETERS
%--------------------------------------------------------------------------
CONTROL.PARAM.DIST_THRESHOLD = 1*10e2; % Radious of 1000 ft to detect target
% CONTROL.PARAM.DIST_OBSTACLE = 12152.2; % (ft) radius around boats 2 nautical miles 
CONTROL.PARAM.DIST_OBSTACLE = 1519.029*1; % (ft) radius around boats 0.25 nautical miles MULTIPLIED BY 4 TO GET CLOSE TO WP IN MEDEVAC
% CONTROL.PARAM.DIST_GOAL = 3797.5722; % (ft) WP reached {In my code used to be 10}

CONTROL.PARAM.FVAL = 0;
CONTROL.PARAM.EXITVAL = 0;

if (SCENARIO_CONTROL_MODE == 0) % MEDEVAC
    CONTROL.PARAM.CBF_CONST = 0.01*7; % For BELL 207 {MEDEVAC constant Value}
    CONTROL.PARAM.CBF_H = zeros(1,1);
    CONTROL.PARAM.CBF_HDOT = zeros(1,1);
    CONTROL.PARAM.CBF_PSI = zeros(1,1);
    CONTROL.PARAM.CBF_A1QP = zeros(1,1);
    CONTROL.PARAM.CBF_A2QP = zeros(1,1);
    CONTROL.PARAM.CBF_B1QP = zeros(1,1);
else % ISR
    CONTROL.PARAM.CBF_CONST = 0.2; % For OSPREY {ISR constant Value} {ISR 1st round 0.2}
    CONTROL.PARAM.CBF_H = zeros(20,1);
    CONTROL.PARAM.CBF_HDOT = zeros(20,1);
    CONTROL.PARAM.CBF_PSI = zeros(20,1);
    CONTROL.PARAM.CBF_A1QP = zeros(20,1);
    CONTROL.PARAM.CBF_A2QP = zeros(20,1);
    CONTROL.PARAM.CBF_B1QP = zeros(20,1);
end


%--------------------------------------------------------------------------
% INITIALZIATION
%--------------------------------------------------------------------------
CONTROL.PARAM.NAV_D_1 = 10;
CONTROL.PARAM.NAV_D_2 = 10;
% Aircraft Altitude (feet)
CONTROL.PARAM.ALTITUDE = 1.5e3;
CONTROL.PARAM.ALTITUDE_REF = CONTROL.PARAM.ALTITUDE;
CONTROL.PARAM.RHO = 20.902e6 + CONTROL.PARAM.ALTITUDE; % feet
%CONTROL.OUTPUT.ALTITUDE = 0;
CONTROL.PARAM.VERTICAL_SPEED =17; % (feet/s)
%--------------------------------------------------------------------------
% CONTROL TARGET
%--------------------------------------------------------------------------
% Targets for navigation
CONTROL.TARGET.SIMU_END = 0;
CONTROL.TARGET.LATITUDE = 0;
CONTROL.TARGET.LONGITUDE = 0;

if (SCENARIO_CONTROL_MODE == 0) % MEDEVAC
    CONTROL.TARGET.VELOCITY = 236.93; % Bell 407 - feet/sec 
    CONTROL.TARGET.WAYPOINT_VERIFIED = 0;
    CONTROL.TARGET.OBSTACLE_THREATCLASS = ones(1,1);
else % ISR
    % CONTROL.TARGET.VELOCITY = 303.806; % OSPREY - feet/sec
    CONTROL.TARGET.VELOCITY = 455.709; % OSPREY - feet/sec 
    % Obstacles to avoid
    CONTROL.TARGET.OBSTACLE_ID = zeros(20,1);
    CONTROL.TARGET.OBSTACLE_LATITUDE = zeros(20,1);
    CONTROL.TARGET.OBSTACLE_LONGITUDE = zeros(20,1);
    CONTROL.TARGET.OBSTACLE_TARGETCLASS = ones(20,1); % 1 = AVOID, 0 = FLY OVER
    CONTROL.TARGET.OBSTACLE_THREATCLASS = ones(20,1);
    CONTROL.TARGET.OBSTACLE_COORD1 = zeros(20,1);
    CONTROL.TARGET.OBSTACLE_COORD2 = zeros(20,1);
end

CONTROL.TARGET.HUMAN_ATT_MODE = HUMAN_ATT_MODE;
CONTROL.PARAM.CBF_CONST_ATT = ones(1,1);

CONTROL.PARAM.DIST_P = MODEL.PARAM.DISP_P;
CONTROL.OUTPUT.UA = 0;
CONTROL.OUTPUT.UALPHA = 0;



% % MEDEVAC SCENARIO
% % rho = 20.902e6 + 2*10e2; % During flight 
% % TARGET_POS1(1) = rho*cos(phi_lat)*cos(theta_long);
% % TARGET_POS2(1) = rho*cos(phi_lat)*sin(theta_long);
% 
% % CHILDRN HLTH CARE ATL SCOTTISH RITE
% % LAT: 33.906866054481476 = 5.9179e-01, LONG: -84.35439102319383= -1.4723e+00
% CONTROL.TARGET.TARGET_POS1(1) = 1.7061e+06;
% CONTROL.TARGET.TARGET_POS2(1) = -1.7265e+07;
% 
% % EMORY UNIVERSITY HOSPITAL MIDTOWN
% % LAT: 33.76878595666145 = 5.8938e-01, LOG = -84.38688413060517 = -1.4728e+00
% CONTROL.TARGET.TARGET_POS1(2) = 1.7002e+06;
% CONTROL.TARGET.TARGET_POS2(2) = -1.7294e+07;
% 
% % % WP 1: LAT = 0.589, LONG = -1.47
% % CONTROL.TARGET.TARGET_POS1(1) = 1.7490e+06;
% % CONTROL.TARGET.TARGET_POS2(1) = -1.7293e+07;
% % 
% % % WP2: LAT = 0.5895 , LONG = -1.47
% % CONTROL.TARGET.TARGET_POS1(2) = 1.7485e+06;
% % CONTROL.TARGET.TARGET_POS2(2) = -1.7288e+07;
% % 
% % % WP3: LAT = 0.59 , LONG = -1.469
% % CONTROL.TARGET.TARGET_POS1(3) = 1.7651e+06;
% % CONTROL.TARGET.TARGET_POS2(3) = -1.7280e+07;

%--------------------------------------------------------------------------
% CONTROL OUTPUT
%--------------------------------------------------------------------------
% Virtual Controller Input Tau1
CONTROL.OUTPUT.TAU1 = 0;
% Virtual Controller Input Tau2
CONTROL.OUTPUT.TAU2 = 0;
% Virtual Nominal Controller Input Tau1
CONTROL.OUTPUT.TAU1_NOM = 0;
% Virtual Nominal Controller Input Tau2
CONTROL.OUTPUT.TAU2_NOM = 0;

% Spherical coordinates relations:
% x1 = rho*cos(phi)*cos(theta)
% x2 = rho*cos(phi)*sin(theta)
% Aircraft Latitude (rad)
CONTROL.OUTPUT.LATITUDE = 0;
% Aircraft Longitude (rad)
CONTROL.OUTPUT.LONGITUDE = 0;
% Aircraft Heading (deg)
CONTROL.OUTPUT.HEADING = 0;
% Aircraft Heading NED (deg)
CONTROL.OUTPUT.HEADING_NED = 0;
% Aircraft Velorcity NED 
CONTROL.OUTPUT.NED_VY1 = 0;
CONTROL.OUTPUT.NED_VY2 = 0;
return