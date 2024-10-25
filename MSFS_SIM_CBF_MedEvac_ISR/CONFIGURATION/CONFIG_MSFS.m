%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CONFIG MSFS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clc
clear
format short e
warning ('off', 'all')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% GENERAL CONFIGURATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SCENARIO MODE: 0 - MEDEVAC / 1 - ISR
SCENARIO_CONTROL_MODE = 1;
% HUMAN ATTENTIVENESS: 0 - OFF / 1 - ON
HUMAN_ATT_MODE = 0;
% SIM CONTROL MODE: 0 - TRACKING ONLY / 1 - CBFS + TRACKING
SIM_CONTROL_MODE = 1;
% COMMUNICATIONS MODE: 0 - LOCAL / 1 - SERVER
COMMUNICATIONS_MODE = 1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MODEL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
SAMPLING_TIME = 30e-3;
cd ../SOFTWARE_COMPONENTS/MODEL
MODEL_INI = CONFIG_MODEL(SAMPLING_TIME,SCENARIO_CONTROL_MODE,HUMAN_ATT_MODE);
cd ../../CONFIGURATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% CONTROL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
cd ../SOFTWARE_COMPONENTS/CONTROL
CONTROL_INI = CONFIG_CONTROL(MODEL_INI,SIM_CONTROL_MODE,SCENARIO_CONTROL_MODE,HUMAN_ATT_MODE);
cd ../../CONFIGURATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% BUS DEFINITIONS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
cd ../BUS_DEFINITIONS
BusDefinition(MODEL_INI, 'MODEL_Bus')
BusDefinition(CONTROL_INI, 'CONTROL_Bus')
cd ../CONFIGURATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% SIMULINK MODEL CONFIGURATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
cd ('../SIMULINK')
PC_SLX = 'PC_MSFS_STATION';
open(PC_SLX)
set_param(PC_SLX, 'FixedStep', num2str(MODEL_INI.PARAM.SIM_SAMPLING_TIME));
set_param(PC_SLX, 'StopTime', num2str(MODEL_INI.PARAM.SIM_FINAL_TIME));
% set_param([PC_MSFS_STATION 'SUBSYSTEM_NAME'], 'Commented', 'on');
set_param(PC_SLX, 'SimulationMode', 'Normal');
if (SCENARIO_CONTROL_MODE == 0) % MEDEVAC
    set_param('PC_MSFS_STATION/SYSTEM/MEDEVAC', 'Commented', 'off');
    set_param('PC_MSFS_STATION/SYSTEM/ISR', 'Commented', 'on');
    set_param('PC_MSFS_STATION/CONTROL/MEDEVAC', 'Commented', 'off');
    set_param('PC_MSFS_STATION/CONTROL/ISR', 'Commented', 'on');
    set_param('PC_MSFS_STATION/MSFS/MEDEVAC', 'Commented', 'off');
    set_param('PC_MSFS_STATION/MSFS/ISR', 'Commented', 'on');
    if (COMMUNICATIONS_MODE == 0) % Local
        set_param('PC_MSFS_STATION/MSFS/MEDEVAC/COMMUNICATIONS/LOCAL COMMUNICATIONS', 'Commented', 'off');
        set_param('PC_MSFS_STATION/MSFS/MEDEVAC/COMMUNICATIONS/SERVER COMMUNICATIONS', 'Commented', 'on');
    else % Server
        set_param('PC_MSFS_STATION/MSFS/MEDEVAC/COMMUNICATIONS/LOCAL COMMUNICATIONS', 'Commented', 'on');
        set_param('PC_MSFS_STATION/MSFS/MEDEVAC/COMMUNICATIONS/SERVER COMMUNICATIONS', 'Commented', 'off');
    end
else % ISR
    set_param('PC_MSFS_STATION/SYSTEM/MEDEVAC', 'Commented', 'on');
    set_param('PC_MSFS_STATION/SYSTEM/ISR', 'Commented', 'off');
    set_param('PC_MSFS_STATION/CONTROL/MEDEVAC', 'Commented', 'on');
    set_param('PC_MSFS_STATION/CONTROL/ISR', 'Commented', 'off');
    set_param('PC_MSFS_STATION/MSFS/MEDEVAC', 'Commented', 'on');
    set_param('PC_MSFS_STATION/MSFS/ISR', 'Commented', 'off');
    if (COMMUNICATIONS_MODE == 0) % Local
        set_param('PC_MSFS_STATION/MSFS/ISR/COMMUNICATIONS/LOCAL COMMUNICATIONS', 'Commented', 'off');
        set_param('PC_MSFS_STATION/MSFS/ISR/COMMUNICATIONS/SERVER COMMUNICATIONS', 'Commented', 'on');
    else % Server
        set_param('PC_MSFS_STATION/MSFS/ISR/COMMUNICATIONS/LOCAL COMMUNICATIONS', 'Commented', 'on');
        set_param('PC_MSFS_STATION/MSFS/ISR/COMMUNICATIONS/SERVER COMMUNICATIONS', 'Commented', 'off');
    end
end



