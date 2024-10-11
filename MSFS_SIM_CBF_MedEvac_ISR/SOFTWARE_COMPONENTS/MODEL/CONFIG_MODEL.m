function MODEL = CONFIG_MODEL(SAMPLING_TIME,SCENARIO_CONTROL_MODE,HUMAN_ATT_MODE)
%--------------------------------------------------------------------------
% GENERAL PARAMETERS
%--------------------------------------------------------------------------
% Control sampling time (s)
MODEL.PARAM.SAMPLING_TIME = SAMPLING_TIME;
% Simulation sampling time (s)
MODEL.PARAM.SIM_SAMPLING_TIME = SAMPLING_TIME;
% Simulation final time (s)
MODEL.PARAM.SIM_FINAL_TIME = 2000;
MODEL.PARAM.FLIGHT_STATUS = 0;
MODEL.PARAM.HEADING_OFFSET = 3*pi/180*0;
MODEL.PARAM.RESET_POS = 0;
%--------------------------------------------------------------------------
% HUMAN ATTENTIVENESS
%--------------------------------------------------------------------------
MODEL.PARAM.HUMAN_ATT_MODE = HUMAN_ATT_MODE;
MODEL.PARAM.ATT_SCALE_FACTOR = 1*1;
MODEL.INPUT.ATT_VALUE = 0;
MODEL.PARAM.ATT_SAT_FLAG = 0;
MODEL.AUX.ALPHA_DOT = 0;
MODEL.AUX.ALPHA = 0;
MODEL.AUX.PATH_FOLLOWED = 0;
MODEL.AUX.ATT_VAL_USED = 0;
%--------------------------------------------------------------------------
% SECOND ORDER UNICYCLE PARAMETERS
%--------------------------------------------------------------------------
% Displaced point distance (ft)
MODEL.PARAM.DISP_P = 0.05;
%--------------------------------------------------------------------------
% MODEL INPUT
%--------------------------------------------------------------------------
% Virtual Controller Input Tau1
MODEL.INPUT.TAU1 = 0;
% Virtual Controller Input Tau2
MODEL.INPUT.TAU2 = 0;
if (SCENARIO_CONTROL_MODE == 0) % MEDEVAC
    % Aircraft Altitude (feet) - INITIAL CONDITION
    MODEL.INPUT.ALTITUDE = 1.5e3;
    % Aircraft Latitude (rad) - INITIAL CONDITION
    MODEL.INPUT.LATITUDE = 33.6595539*pi/180; % Miller Farm Airport
    % Aircraft Longitude (rad) - INITIAL CONDITION
    MODEL.INPUT.LONGITUDE = -84.6629889*pi/180; % Miller Farm Airport
else % ISR
    % Aircraft Altitude (feet) - INITIAL CONDITION
    MODEL.INPUT.ALTITUDE = 1.5e3;
    % Aircraft Latitude (rad) - INITIAL CONDITION
    % MODEL.INPUT.LATITUDE = 33.76266931552261*pi/180; % San Diego Navy Airport
    % MODEL.INPUT.LATITUDE = 32.636*pi/180; % AG01 
    MODEL.INPUT.LATITUDE = 33*pi/180; % CENTER OF SEARCH GRID
    % Aircraft Longitude (rad) - INITIAL CONDITION
    % MODEL.INPUT.LONGITUDE = -84.37393441343322*pi/180; % San Diego Navy Airport
    % MODEL.INPUT.LONGITUDE = -117.23*pi/180; % AG01
    MODEL.INPUT.LONGITUDE = -118*pi/180; % CENTER OF SEARCH GRID
end


MODEL.PARAM.INIT_LAT = MODEL.INPUT.LATITUDE;
MODEL.PARAM.INIT_LONG = MODEL.INPUT.LONGITUDE;
MODEL.PARAM.FIRST_IT = zeros(1,1);
%--------------------------------------------------------------------------
% MODEL OUTPUT
%--------------------------------------------------------------------------
% Aircraft Altitude (feet)
MODEL.OUTPUT.ALTITUDE = MODEL.INPUT.ALTITUDE;
% Aircraft Latitude (rad)
MODEL.OUTPUT.LATITUDE = MODEL.INPUT.LATITUDE;
% Aircraft Longitude (rad)
MODEL.OUTPUT.LONGITUDE = MODEL.INPUT.LONGITUDE;
% Aircraft pitch (radians)
MODEL.OUTPUT.PITCH = pi*0;
% Aircraft Heading (radians)
MODEL.OUTPUT.HEADING = 0; 
MODEL.OUTPUT.HEADING_NED = 0;
% INITIAL CONDITIONS - POSITION
rho = 20.902e6 + MODEL.INPUT.ALTITUDE;
% (X1, X2) = (rho*cos(phi_lat)*cos(theta_long), rho*cos(phi_lat)*sin(theta_long));
% Center of Mass Position x1
MODEL.OUTPUT.X1 = rho*cos(MODEL.INPUT.LATITUDE)*cos(MODEL.INPUT.LONGITUDE);
% Center of Mass Position x2
MODEL.OUTPUT.X2 =  rho*cos(MODEL.INPUT.LATITUDE)*sin(MODEL.INPUT.LONGITUDE);
%--------------------------------------------------------------------------
% STATES
%--------------------------------------------------------------------------
% Displaced Point Dynamics Y = {y1, y2, vy1, vy2} - 1 TO 4
% Unicycle Dynamics X = {s, theta, omega} - 5 TO 7
% y1 = STATE(1)
% y2 = STATE(2)
% vy1 = STATE(3)
% vy2 = STATE(4)
% s = STATE(5)
% theta = STATE(6)
% omega = STATE(7)
% alpha = STATE(8) Extended state for RT CBFs

% if HUMAN_ATT_MODE == 0
%     MODEL.STATE = zeros(7,1);
%     MODEL.PARAM.INIT_STATE = zeros(7,1);
%     MODEL.STATE(5) = 0;
%     MODEL.STATE(6) = 0;
%     MODEL.STATE(7) = 0;
%     MODEL.STATE(1) = MODEL.OUTPUT.X1 + MODEL.PARAM.DISP_P*cos(MODEL.STATE(6));
%     MODEL.STATE(2) = MODEL.OUTPUT.X2 + MODEL.PARAM.DISP_P*sin(MODEL.STATE(6));
%     MODEL.STATE(3) =  MODEL.STATE(5)*cos(MODEL.STATE(6)) - MODEL.PARAM.DISP_P*MODEL.STATE(7)*sin(MODEL.STATE(6));
%     MODEL.STATE(4) =  MODEL.STATE(5)*sin(MODEL.STATE(6)) + MODEL.PARAM.DISP_P*MODEL.STATE(7)*cos(MODEL.STATE(6));
%     % Output x = sqrt(x1^2 + x2^2)
%     MODEL.OUTPUT.X = sqrt(MODEL.OUTPUT.X1^2 + MODEL.OUTPUT.X2^2);
%     % Output y = sqrt(y1^2 + y2^2)
%     MODEL.OUTPUT.Y = sqrt(MODEL.STATE(1)^2 + MODEL.STATE(2)^2);
% else
    MODEL.STATE = zeros(8,1);
    MODEL.PARAM.INIT_STATE = zeros(8,1);
    MODEL.STATE(5) = 0;
    MODEL.STATE(6) = 0;
    MODEL.STATE(7) = 0;
    MODEL.STATE(8) = 1;
    MODEL.STATE(1) = MODEL.OUTPUT.X1 + MODEL.PARAM.DISP_P*cos(MODEL.STATE(6));
    MODEL.STATE(2) = MODEL.OUTPUT.X2 + MODEL.PARAM.DISP_P*sin(MODEL.STATE(6));
    MODEL.STATE(3) =  MODEL.STATE(5)*cos(MODEL.STATE(6)) - MODEL.PARAM.DISP_P*MODEL.STATE(7)*sin(MODEL.STATE(6));
    MODEL.STATE(4) =  MODEL.STATE(5)*sin(MODEL.STATE(6)) + MODEL.PARAM.DISP_P*MODEL.STATE(7)*cos(MODEL.STATE(6));
    % Output x = sqrt(x1^2 + x2^2)
    MODEL.OUTPUT.X = sqrt(MODEL.OUTPUT.X1^2 + MODEL.OUTPUT.X2^2);
    % Output y = sqrt(y1^2 + y2^2)
    MODEL.OUTPUT.Y = sqrt(MODEL.STATE(1)^2 + MODEL.STATE(2)^2);
% end

MODEL.PARAM.INIT_STATE(:) = MODEL.STATE(:);
return