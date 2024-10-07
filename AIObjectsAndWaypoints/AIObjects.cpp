//------------------------------------------------------------------------------
//
//  SimConnect AI Objects sample -- Modified for more complex creation of ships
//  
//------------------------------------------------------------------------------

#include <algorithm>
#include <csignal>
#include <cmath>
#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <strsafe.h>
#include <string>
#include <vector>
#include <iostream>
#include <cstdlib>
#include <fstream>
//#include <bits/stdc++.h>

#include "SimConnect.h"

int     quit = 0;
HANDLE  hSimConnect = NULL;
DWORD   SHIPKNZYID = SIMCONNECT_OBJECT_ID_USER;

using namespace std;

static enum EVENT_ID {
	EVENT_SIM_START,
	EVENT_Z,
	EVENT_X,
	EVENT_C,
	EVENT_NUM1,
	EVENT_NUM2,
	EVENT_NUM3,
	EVENT_NUM4,
	EVENT_NUM5,
	EVENT_NUM6,
	EVENT_NUM7,
	EVENT_NUM8,
	EVENT_NUM9,
	EVENT_NUM0,
};

static enum DATA_REQUEST_ID {
	REQUEST_ADD_SHIPKNZY,
	REQUEST_REMOVE_SHIPKNZY
};

static enum GROUP_ID {
	GROUP_ZX,
};

static enum INPUT_ID {
	INPUT_ZX,
};

static enum DEFINITION_ID {
	DEFINITION_WAYPOINT
};

// Set up flags so these operations only happen once
static bool plansSent = false;
static bool	objectsCreated = false;
int numShips = 0;

std::string waypoints = "";
int initialShipID = -1;
const int numWaypoints = 30;

vector<double> xys;  // vector of doubles, do some algebra to get x y s for each ship and waypoint
double scale = 86.4 * 0.1;  // scale of the spawn board
double shiftWest = 0;  // shift west, keep this small
double shiftNorth = 0;  // shift north, keep this small

// from http://www.digitalpeer.com/blog/simple
vector<string> tokenize(const string& str, const string& delimiters)
{
	vector<string> tokens;

	// skip delimiters at beginning.
	string::size_type lastPos = str.find_first_not_of(delimiters, 0);

	// find first "non-delimiter".
	string::size_type pos = str.find_first_of(delimiters, lastPos);

	while (string::npos != pos || string::npos != lastPos)
	{
		// found a token, add it to the vector.
		tokens.push_back(str.substr(lastPos, pos - lastPos));

		// skip delimiters.  Note the "not_of"
		lastPos = str.find_first_not_of(delimiters, pos);

		// find next "non-delimiter"
		pos = str.find_first_of(delimiters, lastPos);
	}

	return tokens;
}

void sendFlightPlans(int shipIdx)
{
	HRESULT hr;
	
	SIMCONNECT_DATA_WAYPOINT    waypointListShipKNZY[numWaypoints];

	// add each waypoint
	for (int w = 1; w < numWaypoints; w++) {
		// get the values for this ship and waypoint
		double x = xys[shipIdx * numWaypoints * 3 + w * 3 + 0];
		double y = xys[shipIdx * numWaypoints * 3 + w * 3 + 1];
		double s = xys[shipIdx * numWaypoints * 3 + w * 3 + 2];
		if (s == 0) {
			return;
			//s = 100;
		}
		//cout << "Waypoint " << x << " " << y << " " << s << endl;

		waypointListShipKNZY[w-1].Flags = SIMCONNECT_WAYPOINT_SPEED_REQUESTED;
		waypointListShipKNZY[w-1].Altitude = 0;
		waypointListShipKNZY[w-1].Latitude = 33 - ((y - .5) * scale) / 60.0 + shiftWest;
		waypointListShipKNZY[w-1].Longitude = -118 + ((x - .5) * scale) / 60.0 + shiftNorth;
		waypointListShipKNZY[w-1].ktsSpeed = s;
	}

	waypointListShipKNZY[numWaypoints-1].Flags = SIMCONNECT_WAYPOINT_SPEED_REQUESTED;
	waypointListShipKNZY[numWaypoints-1].Altitude = 0;
	waypointListShipKNZY[numWaypoints-1].Latitude = 33 - ((.75 - .5) * scale) / 60.0 + shiftWest;
	waypointListShipKNZY[numWaypoints-1].Longitude = -118 + ((.75 - .5) * scale) / 60.0 + shiftNorth;
	waypointListShipKNZY[numWaypoints-1].ktsSpeed = 0;

	hr = SimConnect_SetDataOnSimObject(hSimConnect, DEFINITION_WAYPOINT, SHIPKNZYID, 0, ARRAYSIZE(waypointListShipKNZY), sizeof(waypointListShipKNZY[0]), waypointListShipKNZY);
}

void setUpSimObjects(int num)
{
	SIMCONNECT_DATA_INITPOSITION Init;
	HRESULT hr;
	numShips = num;
	for (int i = 0; i < num; i++)
	{
		// pull the ship position
		double x = xys[i * numWaypoints * 3 + 0];
		double y = xys[i * numWaypoints * 3 + 1];
		double s = xys[i * numWaypoints * 3 + 2];

		double x_next = xys[i * numWaypoints * 3 + 3];
		double y_next = xys[i * numWaypoints * 3 + 4];
		double s_next = xys[i * numWaypoints * 3 + 5];

		Init.Altitude = 0.0;
		Init.Latitude = 33 - ((y-.5) * scale) / 60.0 + shiftWest;
		Init.Longitude = -118 + ((x-.5) * scale) / 60.0 + shiftNorth;
		Init.Pitch = 0.0;
		Init.Bank = 0.0;
		Init.Heading = atan2(y_next - y, x_next - x) * 180 / 3.14159 + 180;  // degrees
		Init.OnGround = 1;
		Init.Airspeed = 0;
		int type = rand() % 3;
		if (type > 0)
		{
			if (type == 2)
			{
				hr = SimConnect_AICreateSimulatedObject(hSimConnect, "Yacht01", Init, REQUEST_ADD_SHIPKNZY);
			}
			else hr = SimConnect_AICreateSimulatedObject(hSimConnect, "CargoShip01", Init, REQUEST_ADD_SHIPKNZY);
		}
		else hr = SimConnect_AICreateSimulatedObject(hSimConnect, "FishingBoat", Init, REQUEST_ADD_SHIPKNZY);
	}
	
}

void removeSimObjects() {
	
	HRESULT hr;
	for (int i = 0; i < numShips; i++)
	{


		if (SHIPKNZYID != SIMCONNECT_OBJECT_ID_USER) {
			hr = SimConnect_AIRemoveObject(hSimConnect, SHIPKNZYID, REQUEST_REMOVE_SHIPKNZY);
			printf("\nRemoved SHIPKNZY id = %d", SHIPKNZYID);
		}
		SHIPKNZYID = (DWORD)((int)SHIPKNZYID - 1);
	}
}

static const char* ExceptionName(SIMCONNECT_EXCEPTION exception) {
	switch (exception) {
	case SIMCONNECT_EXCEPTION_NONE:				//0
		return "EXCEPTION_NONE (0)";
	case SIMCONNECT_EXCEPTION_ERROR:			//1
		return "EXCEPTION_ERROR (1)";
	case SIMCONNECT_EXCEPTION_SIZE_MISMATCH:	//2
		return "EXCEPTION_SIZE_MISMATCH (2)";
	case SIMCONNECT_EXCEPTION_UNRECOGNIZED_ID:	//3
		return "EXCEPTION_UNRECOGNIZED_ID (3)";
	case SIMCONNECT_EXCEPTION_UNOPENED:			//4
		return "EXCEPTION_UNOPENED (4)";
	case SIMCONNECT_EXCEPTION_VERSION_MISMATCH:	//5
		return "EXCEPTION_VERSION_MISMATCH (5)";
	case SIMCONNECT_EXCEPTION_TOO_MANY_GROUPS:	//6
		return "EXCEPTION_TOO_MANY_GROUPS (6)";
	case SIMCONNECT_EXCEPTION_NAME_UNRECOGNIZED://7
		return "EXCEPTION_NAME_UNRECOGNIZED (7)";
	case SIMCONNECT_EXCEPTION_TOO_MANY_EVENT_NAMES:		//8
		return "EXCEPTION_TOO_MANY_EVENT_NAMES (8)";
	case SIMCONNECT_EXCEPTION_EVENT_ID_DUPLICATE:		//9
		return "EXCEPTION_EVENT_ID_DUPLICATE (9)";
	case SIMCONNECT_EXCEPTION_TOO_MANY_MAPS:			//10
		return "EXCEPTION_TOO_MANY_MAPS (10)";
	case SIMCONNECT_EXCEPTION_TOO_MANY_OBJECTS:			//11
		return "EXCEPTION_TOO_MANY_OBJECTS (11)";
	case SIMCONNECT_EXCEPTION_TOO_MANY_REQUESTS:				//12
		return "EXCEPTION_TOO_MANY_REQUESTS (12)";
	case SIMCONNECT_EXCEPTION_WEATHER_INVALID_PORT:				//13
		return "EXCEPTION_WEATHER_INVALID_PORT (13)";
	case SIMCONNECT_EXCEPTION_WEATHER_INVALID_METAR:			//14
		return "EXCEPTION_WEATHER_INVALID_METAR (14)";
	case SIMCONNECT_EXCEPTION_WEATHER_UNABLE_TO_GET_OBSERVATION://15
		return "EXCEPTION_WEATHER_UNABLE_TO_GET_OBSERVATION (15)";
	case SIMCONNECT_EXCEPTION_WEATHER_UNABLE_TO_CREATE_STATION:	//16
		return "EXCEPTION_WEATHER_UNABLE_TO_CREATE_STATION (16)";
	case SIMCONNECT_EXCEPTION_WEATHER_UNABLE_TO_REMOVE_STATION:	//17
		return "EXCEPTION_WEATHER_UNABLE_TO_REMOVE_STATION (17)";
	case SIMCONNECT_EXCEPTION_INVALID_DATA_TYPE:				//18
		return "EXCEPTION_INVALID_DATA_TYPE (18)";
	case SIMCONNECT_EXCEPTION_INVALID_DATA_SIZE:				//19
		return "EXCEPTION_INVALID_DATA_SIZE (19)";
	case SIMCONNECT_EXCEPTION_DATA_ERROR:						//20
		return "EXCEPTION_DATA_ERROR (20)";
	case SIMCONNECT_EXCEPTION_INVALID_ARRAY:			//21
		return "EXCEPTION_INVALID_ARRAY (21)";
	case SIMCONNECT_EXCEPTION_CREATE_OBJECT_FAILED:		//22
		return "EXCEPTION_CREATE_OBJECT_FAILED (22)";
	case SIMCONNECT_EXCEPTION_LOAD_FLIGHTPLAN_FAILED:	//23
		return "EXCEPTION_LOAD_FLIGHTPLAN_FAILED (23)";
	case SIMCONNECT_EXCEPTION_OPERATION_INVALID_FOR_OBJECT_TYPE://24
		return "EXCEPTION_OPERATION_INVALID_FOR_OBJECT_TYPE (24)";
	case SIMCONNECT_EXCEPTION_ILLEGAL_OPERATION:				//25
		return "EXCEPTION_ILLEGAL_OPERATION (25)";
	case SIMCONNECT_EXCEPTION_ALREADY_SUBSCRIBED:				//26
		return "EXCEPTION_ALREADY_SUBSCRIBED (26)";
	case SIMCONNECT_EXCEPTION_INVALID_ENUM:						//27
		return "EXCEPTION_INVALID_ENUM (27)";
	case SIMCONNECT_EXCEPTION_DEFINITION_ERROR:	//28
		return "EXCEPTION_DEFINITION_ERROR (28)";
	case SIMCONNECT_EXCEPTION_DUPLICATE_ID:		//29
		return "EXCEPTION_DUPLICATE_ID (29)";
	case SIMCONNECT_EXCEPTION_DATUM_ID:			//30
		return "EXCEPTION_DATUM_ID (30)";
	case SIMCONNECT_EXCEPTION_OUT_OF_BOUNDS:	//31
		return "EXCEPTION_OUT_OF_BOUNDS (31)";
	case SIMCONNECT_EXCEPTION_ALREADY_CREATED:	//32
		return "EXCEPTION_ALREADY_CREATED (32)";
	case SIMCONNECT_EXCEPTION_OBJECT_OUTSIDE_REALITY_BUBBLE://33
		return "EXCEPTION_OBJECT_OUTSIDE_REALITY_BUBBLE (33)";
	case SIMCONNECT_EXCEPTION_OBJECT_CONTAINER:				//34
		return "EXCEPTION_OBJECT_CONTAINER (34)";
	case SIMCONNECT_EXCEPTION_OBJECT_AI:					//35
		return "EXCEPTION_OBJECT_AI (35)";
	case SIMCONNECT_EXCEPTION_OBJECT_ATC:					//36
		return "EXCEPTION_OBJECT_ATC (36)";
	case SIMCONNECT_EXCEPTION_OBJECT_SCHEDULE:				//37
		return "EXCEPTION_OBJECT_SCHEDULE (37)";
	default:
		return "UNKNOWN EXCEPTION";
	}
}

void CALLBACK MyDispatchProcSO(SIMCONNECT_RECV* pData, DWORD cbData, void* pContext)
{
	HRESULT hr;

	switch (pData->dwID)
	{
	case SIMCONNECT_RECV_ID_EVENT:
	{
		SIMCONNECT_RECV_EVENT* evt = (SIMCONNECT_RECV_EVENT*)pData;

		switch (evt->uEventID)
		{
		case EVENT_Z:
			if (!objectsCreated)
			{
				setUpSimObjects(10);
				objectsCreated = true;
				
			}
			break;

		case EVENT_X:
			if (!plansSent && objectsCreated)
			{
				plansSent = true;
			}
			break;
		case EVENT_C:
			if (objectsCreated)
			{
				removeSimObjects();
				objectsCreated = false;
				plansSent = false;
			}
			break;
		case EVENT_NUM0:
			if (!objectsCreated)
			{
				setUpSimObjects(100);
				objectsCreated = true;
				
			}
		case EVENT_NUM1:
			if (!objectsCreated)
			{
				setUpSimObjects(10);
				objectsCreated = true;
				
			}
		case EVENT_NUM2:
			if (!objectsCreated)
			{
				setUpSimObjects(20);
				objectsCreated = true;
				
			}
		case EVENT_NUM3:
			if (!objectsCreated)
			{
				setUpSimObjects(30);
				objectsCreated = true;
			
			}
		case EVENT_NUM4:
			if (!objectsCreated)
			{
				setUpSimObjects(40);
				objectsCreated = true;
				
			}
		case EVENT_NUM5:
			if (!objectsCreated)
			{
				setUpSimObjects(50);
				objectsCreated = true;
				
			}
		case EVENT_NUM6:
			if (!objectsCreated)
			{
				setUpSimObjects(60);
				objectsCreated = true;
				
			}
		case EVENT_NUM7:
			if (!objectsCreated)
			{
				setUpSimObjects(70);
				objectsCreated = true;
				
			}
		case EVENT_NUM8:
			if (!objectsCreated)
			{
				setUpSimObjects(80);
				objectsCreated = true;
				
			}
		case EVENT_NUM9:
			if (!objectsCreated)
			{
				setUpSimObjects(90);
				objectsCreated = true;
				
			}
		default:
			printf("\nUnknown event: %d", evt->uEventID);
			break;
		}
		break;
	}

	case SIMCONNECT_RECV_ID_ASSIGNED_OBJECT_ID:
	{
		SIMCONNECT_RECV_ASSIGNED_OBJECT_ID* pObjData = (SIMCONNECT_RECV_ASSIGNED_OBJECT_ID*)pData;

		switch (pObjData->dwRequestID)
		{
			
		case REQUEST_ADD_SHIPKNZY:
			SHIPKNZYID = pObjData->dwObjectID;
			// if we don't know the first ship ID yet, mark it, this is for indexing in the waypoints array
			if (initialShipID == -1) {
				initialShipID = (int)SHIPKNZYID;
			}

			printf("\nCreated ShipKNZY id = %d", SHIPKNZYID);
			sendFlightPlans(SHIPKNZYID - initialShipID);
			//printf("!!!!! CALLLBACK SENDGLrsetgsdrtgeIGTWERW 111111");
			break;
		default:
			printf("\nUnknown creation %d", pObjData->dwRequestID);
			break;
		}
		break;
	}
	case SIMCONNECT_RECV_ID_QUIT:
	{
		quit = 1;
		break;
	}
	case SIMCONNECT_RECV_ID_EXCEPTION:
	{
		SIMCONNECT_RECV_EXCEPTION* data = (SIMCONNECT_RECV_EXCEPTION*)(pData);
		SIMCONNECT_EXCEPTION exception = (SIMCONNECT_EXCEPTION)(data->dwException);
		printf("\nException: %s", ExceptionName(exception));
		break;
	}
	default:
		printf("\nReceived:%d", pData->dwID);
		break;
	}
}

void testSimObjects()
{
	HRESULT hr;

	if (SUCCEEDED(SimConnect_Open(&hSimConnect, "AI Objects and Waypoints", NULL, 0, 0, 0)))
	{
		printf("\nConnected to Flight Simulator!");

		// Create some private events
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_Z);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_X);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_C);

		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM0);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM1);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM2);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM3);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM4);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM5);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM6);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM7);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM8);
		hr = SimConnect_MapClientEventToSimEvent(hSimConnect, EVENT_NUM9);

		// Link the private events to keyboard keys, and ensure the input events are off
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "Z", EVENT_Z);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "X", EVENT_X);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "C", EVENT_C);

		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "0", EVENT_NUM0);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "1", EVENT_NUM1);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "2", EVENT_NUM2);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "3", EVENT_NUM3);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "4", EVENT_NUM4);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "5", EVENT_NUM5);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "6", EVENT_NUM6);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "7", EVENT_NUM7);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "8", EVENT_NUM8);
		hr = SimConnect_MapInputEventToClientEvent(hSimConnect, INPUT_ZX, "9", EVENT_NUM9);

		hr = SimConnect_SetInputGroupState(hSimConnect, INPUT_ZX, SIMCONNECT_STATE_OFF);

		// Sign up for notifications
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_Z);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_X);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_C);

		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM0);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM1);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM2);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM3);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM4);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM5);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM6);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM7);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM8);
		hr = SimConnect_AddClientEventToNotificationGroup(hSimConnect, GROUP_ZX, EVENT_NUM9);

		// Set up a definition for a waypoint list
		hr = SimConnect_AddToDataDefinition(hSimConnect, DEFINITION_WAYPOINT,
			"AI Waypoint List", "number", SIMCONNECT_DATATYPE_WAYPOINT);

		hr = SimConnect_SetInputGroupState(hSimConnect, INPUT_ZX, SIMCONNECT_STATE_ON);

		setUpSimObjects(std::count_if(waypoints.begin(), waypoints.end(), [](char c) {return c == ';'; })-1); // removed -1 from the end

		// wait forever
		while (0 == quit)
		{
			SimConnect_CallDispatch(hSimConnect, MyDispatchProcSO, NULL);
			Sleep(1);
		}

		hr = SimConnect_Close(hSimConnect);
	}
}

int main(int argc, char* argv[])
{
	printf("The ship spawner has been launched!");
	bool startingWaypoints = false;

	// read in the shift
	string shiftNorthString = "";
	getline(std::cin, shiftNorthString);
	shiftNorth = -1 * stod(shiftNorthString);
	
	string shiftWestString = "";
	getline(std::cin, shiftWestString);
	shiftWest = -1 * stod(shiftWestString);

	string scaleString = "";
	getline(std::cin, scaleString);
	scale = stod(scaleString);

	// read in the waypoints

	waypoints = "";
	getline(std::cin, waypoints);

	cout << "Shift West: " << shiftWest << ", North: " << shiftNorth << endl;

	// convert into a long vector of doubles
	vector<string> ships = tokenize(waypoints, ";");
	numShips = ships.size();
	for (int i = 0; i < ships.size(); i++) {
		vector<string> shipWaypoints = tokenize(ships[i], ",");
		for (int w = 0; w < shipWaypoints.size(); w++) {
			vector<string> pts = tokenize(shipWaypoints[w], "-");
			for (string pt : pts) {
				xys.push_back(stod(pt));
			}
		}
	}

	// generate the ships
	testSimObjects();
	return 0;
}