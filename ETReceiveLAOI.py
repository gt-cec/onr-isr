#------------------------------------------------------------------------------
#   File: ETReceiveData.py
#   Desc: Defines the entry point for the Python Eye Tracker Sample Application - Send TCP
#         Command to Eye Tracker to receive data.
#	Change History:
#      09/28/2020: Created.
#
#  Copyright © 2016 - 2022 Argus Science, LLC.  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#
#  •	Redistributions of source code must retain the above copyright notice,
#		this list of conditions and the following disclaimer.
#  •	Redistributions in binary form must reproduce the above copyright notice,
#		this list of conditions and the following disclaimer in the documentation
#		and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
#  OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#  OF THE POSSIBILITY OF SUCH DAMAGE.
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Import
#------------------------------------------------------------------------------
import sys
import msvcrt
import socket
import array
import struct

import requests

#------------------------------------------------------------------------------
# Definitions
#------------------------------------------------------------------------------
# Command
CMD_GET_VERSION                         =   0x0000
CMD_START_DATAFILE_RECORDING            =   0x0001
CMD_STOP_DATAFILE_RECORDING             =   0x0002
CMD_OPEN_DATAFILE                       =   0x0003
CMD_CLOSE_DATAFILE                      =   0x0004
CMD_SET_XDAT                            =   0x0005
CMD_SET_DATAFILE_NAME					=   0x0006
CMD_SET_CONNECT_TYPE					=   0x0007
CMD_START_SDATA_UDP						=   0x0008
CMD_STOP_SDATA_UDP						=   0x0009
CMD_START_SVIDEO_UDP					=   0x000A
CMD_STOP_SVIDEO_UDP						=   0x000B
CMD_START_RVIDEO_UDP					=   0x000C
CMD_STOP_RVIDEO_UDP						=   0x000D
CMD_START_SVFILE_RECORDING				=   0x000E
CMD_STOP_SVFILE_RECORDING				=   0x000F
CMD_OPEN_SVFILE							=   0x0010
CMD_CLOSE_SVFILE						=   0x0011
CMD_DISPLAY_TPS_FULLSCREEN				=   0x0012
CMD_HIDE_TPS_FULLSCREEN					=   0x0013
CMD_SET_TP_TOTALNUM						=   0x0014
CMD_SHOW_TP								=   0x0015
CMD_HIDE_TP								=   0x0016
CMD_GET_TP_TOTALNUM						=   0x0017
CMD_GET_TP_POS							=   0x0018

CMD_GET_DATAITEM						=   0x0019

CMD_DATA_MSG							=   0x81
CMD_JPEG_MSG							=   0x82

# Response bit for network command
CMD_MASK								=   0x00ffffff
CMD_RSP_BIT								=   0x80000000
CMD_RSP_ERR_BIT							=   0x40000000

# Network Socket Type
SOCKET_TYPE_DEFAULT						=   0
SOCKET_TYPE_SERVER						=   1
SOCKET_TYPE_CMD_TCP						=   2
SOCKET_TYPE_SDATA_TCP					=   3
SOCKET_TYPE_SDATA_UDP					=   4
SOCKET_TYPE_RDATA_TCP					=   5
SOCKET_TYPE_RDATA_UDP					=   6
SOCKET_TYPE_SVIDEO_TCP					=   7
SOCKET_TYPE_SVIDEO_UDP					=   8
SOCKET_TYPE_RVIDEO_TCP					=   9
SOCKET_TYPE_RVIDEO_UDP					=   10

# Message Argus Signature
MSG_ARGUS_SIGNATURE                     =   0x20414753          # " AGS"

# Message Buffer Size
MSG_BUFFER_SIZE							=   256
MSG_HEADER_SIZE							=   56

# TypeCode defination
TYPECODE_SByte							=   5	# An signed 8-bit integral type, values between -128 and 127.
TYPECODE_Byte							=   6	# An unsigned 8-bit integral type, values between 0 and 255.
TYPECODE_Int16							=   7	# An signed 16-bit integral type, values between -32768 and 32767.
TYPECODE_UInt16							=   8	# An unsigned 16-bit integral type, values between 0 and 65535.
TYPECODE_UInt32							=   10	# An unsigned 32-bit integral type, values between 0 and 4294967295.
TYPECODE_Single							=   13	# A floating point type, values ranging from approximately 1.5 x 10 -45 to 3.4 x 10 38 with a precision of 7 digits.


#------------------------------------------------------------------------------
# GetBufByte:   Get byte from Buffer at position BPos
#    Buf		-	Buffer array
#    BPos		-	The position of buffer to get byte value
#    Return     -	Byte Value
#------------------------------------------------------------------------------
def GetBufByte(Buf, BPos):
    VByte = Buf[BPos]
    return VByte


#------------------------------------------------------------------------------
# GetBufWord:   Get word from Buffer at position BPos
#    Buf		-	Buffer array
#    BPos		-	The position of buffer to get word value
#    Return     -	Word Value
#------------------------------------------------------------------------------
def GetBufWord(Buf, BPos):
    VWord = Buf[BPos] + Buf[BPos+1] * 256
    return VWord


#------------------------------------------------------------------------------
# GetBufDWord:  Get double word from Buffer at position BPos
#    Buf		-	Buffer array
#    BPos		-	The position of buffer to get double word value
#    Return     -	Double Word Value
#------------------------------------------------------------------------------
def GetBufDWord(Buf, BPos):
    VDWord = Buf[BPos] + (Buf[BPos+1] + (Buf[BPos+2] + Buf[BPos+3] * 256) * 256) * 256
    return VDWord


#------------------------------------------------------------------------------
# GetBufQWord:  Get quad word from Buffer at position BPos
#    Buf		-	Buffer array
#    BPos		-	The position of buffer to get quad word value
#    Return     -	Quad Word Value
#------------------------------------------------------------------------------
def GetBufQWord(Buf, BPos):
    VQWord = Buf[BPos] + (Buf[BPos+1] + (Buf[BPos+2] + (Buf[BPos+3] + (Buf[BPos+4] + (Buf[BPos+5] + (Buf[BPos+6] + Buf[BPos+7] * 256) * 256) * 256) * 256) * 256) * 256) * 256
    return VQWord


#------------------------------------------------------------------------------
# CalCheckSum:  Calculate Check Sum of Buffer
#    Buf		-	Buffer array
#    BufSize	-	Buffer Size
#    Return		-	Check sum of buffer
#------------------------------------------------------------------------------
def CalCheckSum(Buf, BufSize):
    # Initialize Check Sum    
    CheckSum = 0

	# Calculate Sum of Buffer
    for i in range(0, BufSize):
        CheckSum += Buf[i]

    # Calculate Check Sum in Byte
    CheckSum = (~CheckSum + 1) & 0xFF 

    # Return result
    return CheckSum


#------------------------------------------------------------------------------
# SendETCmd:    Send Command to Eye Tracker
#    CSocket    -   Command Socket connected to Eye Tracker
#    Cmd		-	Command
#    Arg		-	Command Argument
#    Return		-	True if succeeded, False if failed
#------------------------------------------------------------------------------
def SendETCmd(CSocket, Cmd, Arg):
    # Convert Command to byte array in little endian
    CmdArr = Cmd.to_bytes(4, "little")

    # Convert Argument to byte array in little endian
    ArgArr = Arg.to_bytes(4, "little")

    # Set up Command Structure, please check details with Argus Network Protocol
    CmdStruc = [0x53, 0x47, 0x41, 0x20, 20, 0, 0, 0, CmdArr[0], CmdArr[1], CmdArr[2], CmdArr[3], 0, 0, 0, 0, ArgArr[0], ArgArr[1], ArgArr[2], ArgArr[3]]

    # Calculate Check Sum of Command Structure
    CSum = CalCheckSum(bytearray(CmdStruc), 20)
    
    # Convert Check Sum to byte array
    CSumArr = CSum.to_bytes(4, "little")
    
    # Updat command structure checksum
    CmdStruc[12] = CSumArr[0]

    # Try to send command
    try:
        CSocket.send(bytearray(CmdStruc))
    except Exception as e:
        # Return False if failed
        return False

    # Return True if succeeded
    return True


#------------------------------------------------------------------------------
# ProcMsgDataItem:  Process Message Data Item Value
#    Buf		    -	Buffer array
#    iDIndex	    -	Data Item Index
#    iCheckState	-	Data Item CheckState
#    iFlagShift	    -	Data Item CheckState Flag
#    iTypeCode	    -	Data Item Type
#    Return		    -	True if Data Item is available, Fasle if not
#------------------------------------------------------------------------------
def ProcMsgDataItem(Buf, iDIndex, iCheckState, iFlagShift, iTypeCode):
    
    # Return Flag
    FlagRtn = False
    
    # Data Item Value
    Val = bytearray(1)

    # Check State to verify whether Data Item is available
    if (((iCheckState >> iFlagShift) & 1) > 0):

        # Set Return Flag to True if available
        FlagRtn = True

        # Check whether type is signed char
        if (iTypeCode == TYPECODE_SByte):
            ValArr = Buf[iDIndex:(iDIndex+1)]
            Val = struct.unpack('<b', ValArr)
            iDIndex += 1
        # Check whether type is unsigned char
        elif (iTypeCode == TYPECODE_Byte):
            ValArr = Buf[iDIndex:(iDIndex+1)]
            Val = struct.unpack('<B', ValArr)
            iDIndex += 1
        # Check whether type is signed word
        elif (iTypeCode == TYPECODE_Int16):
            ValArr = Buf[iDIndex:(iDIndex+2)]
            Val = struct.unpack('<h', ValArr)
            iDIndex += 2
        # Check whether type is unsigned word
        elif (iTypeCode == TYPECODE_UInt16):
            ValArr = Buf[iDIndex:(iDIndex+2)]
            Val = struct.unpack('<H', ValArr)
            iDIndex += 2
        # Check whether type is float
        elif (iTypeCode == TYPECODE_UInt32):
            ValArr = Buf[iDIndex:(iDIndex+4)]
            Val = struct.unpack('<I', ValArr)
            iDIndex += 4
        # Check whether type is float
        elif (iTypeCode == TYPECODE_Single):
            ValArr = Buf[iDIndex:(iDIndex+4)]
            Val = struct.unpack('<f', ValArr)
            iDIndex += 4
        # Other type not supported
        else:
            FlagRtn = False
    
    # Return result
    return FlagRtn, iDIndex, iFlagShift+1, Val


#------------------------------------------------------------------------------
# ProcMsgDataV0:    Process Eye Tracker Data (Network Protocol Version 0), and display data result
#    Buf		    -	Buffer array to process
#    Return		    -	Buffer array left for future processing
#------------------------------------------------------------------------------
# def ProcMsgDataV0(Buf):
#     # Initialize
#     DataMsgSize = 0
#     CheckState = 0

# 	# Search Argus Signature and get message size
#     for BIndex in range(0, len(Buf) - MSG_HEADER_SIZE):
#         if (GetBufDWord(Buf, BIndex) == MSG_ARGUS_SIGNATURE) & (GetBufWord(Buf, BIndex + 8) == CMD_DATA_MSG):
#             DataMsgSize = GetBufDWord(Buf, BIndex + 4)
#             break

#     # Check the result
#     if (DataMsgSize > 0):
#         # Make sure whole message is available
#         if ((DataMsgSize + BIndex) <= len(Buf)):
#             # Data Item Flag Shift
#             FlagShift = 0

#             # Frame Number
#             DIndex = BIndex + 24
#             print(f"\nFrame Number: {GetBufDWord(Buf, DIndex)}")

#             # Update Rate
#             DIndex += 16
#             print(f"Update Rate: {GetBufDWord(Buf, DIndex)}")

#             # Get Check State of each Data Item
#             DIndex += 8
#             CheckState = GetBufQWord(Buf, DIndex)

#             # Get Check State of each Data Item
#             DIndex += 8
#             Val = 0
#             FlagData = False

# 	        # Get "start_of_record"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Byte)
#             if (FlagData):
#                 print(f"start_of_record: 0x" + '{:X}'.format(Val[0]))

#         	# Get "status"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Byte)

# 	        # Get "overtime_count"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
#             if (FlagData):
#                 print(f"overtime_count: " + '{:d}'.format(Val[0]))

# 	        # Get "mark_value"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Byte)
#             if (FlagData):
#                 print(f"mark_value: " + '{:d}'.format(Val[0]))

# 	        # Get "XDAT"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
#             if (FlagData):
#                 print(f"XDAT: " + '{:d}'.format(Val[0]))

# 	        # Get "CU_video_field_num"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
#             if (FlagData):
#                 print(f"CU_video_field_num: " + '{:d}'.format(Val[0]))

# 	        # Get "pupil_pos_horz"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"pupil_pos_horz: " + '{:.1f}'.format(Val[0]))

# 	        # Get "pupil_pos_vert"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"pupil_pos_vert: " + '{:.1f}'.format(Val[0]))

# 	        # Get "pupil_diam"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"pupil_diam: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "pupil_height"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"pupil_height: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "cr_pos_horz"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"cr_pos_horz: " + '{:.1f}'.format(Val[0]))

# 	        # Get "cr_pos_vert"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"cr_pos_vert: " + '{:.1f}'.format(Val[0]))

# 	        # Get "cr_diam"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"cr_diam: " + '{:.1f}'.format(Val[0]))

# 	        # Get "horz_gaze_coord"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"horz_gaze_coord: " + '{:.1f}'.format(Val[0]*0.1))

# 	        # Get "vert_gaze_coord"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"vert_gaze_coord: " + '{:.1f}'.format(Val[0]*0.1))

# 	        # Get "horz_gaze_offset"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"horz_gaze_offset: " + '{:.1f}'.format(Val[0]))

# 	        # Get "vert_gaze_offset"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"vert_gaze_offset: " + '{:.1f}'.format(Val[0]))

# 	        # Get "hdtrk_X"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"hdtrk_X: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "hdtrk_Y"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"hdtrk_Y: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "hdtrk_Z"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"hdtrk_Z: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "hdtrk_az"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"hdtrk_az: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "hdtrk_el"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"hdtrk_el: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "hdtrk_rl"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"hdtrk_rl: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "ET3S_scene_number"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_SByte)
#             if (FlagData):
#                 print(f"ET3S_scene_number: " + '{:d}'.format(Val[0]))

# 	        # Get "ET3S_gaze_length"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"ET3S_gaze_length: " + '{:.1f}'.format(Val[0]))

# 	        # Get "ET3S_horz_gaze_coord"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"ET3S_horz_gaze_coord: " + '{:.1f}'.format(Val[0]))

# 	        # Get "ET3S_vert_gaze_coord"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"ET3S_vert_gaze_coord: " + '{:.1f}'.format(Val[0]))

# 	        # Get "eyeplot_x"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"eyeplot_x: " + '{:.1f}'.format(Val[0]))

# 	        # Get "eyeplot_y"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"eyeplot_y: " + '{:.1f}'.format(Val[0]))

# 	        # Get "ET3S_eye_location_X"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"ET3S_eye_location_X: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "ET3S_eye_location_Y"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"ET3S_eye_location_Y: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "ET3S_eye_location_Z"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"ET3S_eye_location_Z: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "ET3S_gaze_dir_X"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"ET3S_gaze_dir_X: " + '{:.3f}'.format(Val[0]*0.001))

# 	        # Get "ET3S_gaze_dir_Y"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"ET3S_gaze_dir_Y: " + '{:.3f}'.format(Val[0]*0.001))

# 	        # Get "ET3S_gaze_dir_Z"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"ET3S_gaze_dir_Z: " + '{:.3f}'.format(Val[0]*0.001))

# 	        # Get "aux_sensor_X"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"aux_sensor_X: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "aux_sensor_Y"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"aux_sensor_Y: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "aux_sensor_Z"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"aux_sensor_Z: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "aux_sensor_az"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"aux_sensor_az: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "aux_sensor_el"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"aux_sensor_el: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "aux_sensor_rl"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
#             if (FlagData):
#                 print(f"aux_sensor_rl: " + '{:.2f}'.format(Val[0]*0.01))

# 	        # Get "vergence_angle"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"vergence_angle: " + '{:.2f}'.format(Val[0]))

# 	        # Get "verg_gaze_coord_x"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"verg_gaze_coord_x: " + '{:.2f}'.format(Val[0]))

# 	        # Get "verg_gaze_coord_y"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"verg_gaze_coord_y: " + '{:.2f}'.format(Val[0]))

# 	        # Get "verg_gaze_coord_z_left"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"verg_gaze_coord_z_left: " + '{:.2f}'.format(Val[0]))

# 	        # Get "verg_gaze_coord_z_right"
#             FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
#             if (FlagData):
#                 print(f"verg_gaze_coord_z_right: " + '{:.2f}'.format(Val[0]))

#             # Return Buffer Array that has not been processed
#             return Buf[(DataMsgSize + BIndex):]

#         # Return Buffer Array if not the whole eye data message received
#         return Buf[BIndex:]

#     # Return empty array if there's no Argus Eye Data Message found
#     return Buf[len(Buf):]


#------------------------------------------------------------------------------
# ProcMsgDataV1:    Process Eye Tracker Data (Network Protocol Version 1), and display data result
#    Buf		    -	Buffer array to process
#    Return		    -	Buffer array left for future processing
#------------------------------------------------------------------------------
def ProcMsgDataV1(Buf):
    # Initialize
    DataMsgSize = 0
    CheckState = 0

	# Search Argus Signature and get message size
    for BIndex in range(0, len(Buf) - MSG_HEADER_SIZE):
        if (GetBufDWord(Buf, BIndex) == MSG_ARGUS_SIGNATURE) & (GetBufWord(Buf, BIndex + 8) == CMD_DATA_MSG):
            DataMsgSize = GetBufDWord(Buf, BIndex + 4)
            break

    # Check the result
    if (DataMsgSize > 0):
        # Make sure whole message is available
        if ((DataMsgSize + BIndex) <= len(Buf)):
            # Data Item Flag Shift
            FlagShift = 0

            # Frame Number
            DIndex = BIndex + 24
            print(f"\nFrame Number: {GetBufDWord(Buf, DIndex)}")

            # Update Rate
            DIndex += 16
            print(f"Update Rate: {GetBufDWord(Buf, DIndex)}")

            # Get Check State of each Data Item
            DIndex += 8
            CheckState = GetBufQWord(Buf, DIndex)

            # Get BufStart
            DIndex += 8
            Val = 0
            FlagData = False

            print(DIndex)
            print(FlagShift)

	        # # Get "start_of_record"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Byte)
            # if (FlagData):
            #     print(f"start_of_record: 0x" + '{:X}'.format(Val[0]))

        	# # Get "status"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Byte)

	        # # Get "overtime_count"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
            # if (FlagData):
            #     print(f"overtime_count: " + '{:d}'.format(Val[0]))

	        # # Get "mark_value"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Byte)
            # if (FlagData):
            #     print(f"mark_value: " + '{:d}'.format(Val[0]))

	        # # Get "XDAT"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
            # if (FlagData):
            #     print(f"XDAT: " + '{:d}'.format(Val[0]))

	        # # Get "CU_video_field_num"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
            # if (FlagData):
            #     print(f"CU_video_field_num: " + '{:d}'.format(Val[0]))

	        # # Get "pupil_pos_horz"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"pupil_pos_horz: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "pupil_pos_vert"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"pupil_pos_vert: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "pupil_diam"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"pupil_diam: " + '{:.2f}'.format(Val[0]*0.01) + '/{:.2f}'.format(ValR[0]*0.01))

	        # # Get "pupil_height"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"pupil_height: " + '{:.2f}'.format(Val[0]*0.01) + '/{:.2f}'.format(ValR[0]*0.01))

	        # # Get "cr_pos_horz"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"cr_pos_horz: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "cr_pos_vert"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"cr_pos_vert: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "cr_diam"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"cr_diam: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "cr2_pos_horz"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"cr2_pos_horz: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "cr2_pos_vert"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"cr2_pos_vert: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "cr2_diam"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"cr2_diam: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "horz_gaze_coord"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"horz_gaze_coord: " + '{:.1f}'.format(Val[0]*0.1))

	        # # Get "vert_gaze_coord"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"vert_gaze_coord: " + '{:.1f}'.format(Val[0]*0.1))

	        # # Get "horz_gaze_offset"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"horz_gaze_offset: " + '{:.1f}'.format(Val[0]))

	        # # Get "vert_gaze_offset"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"vert_gaze_offset: " + '{:.1f}'.format(Val[0]))

	        # # Get "vergence_angle"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"vergence_angle: " + '{:.2f}'.format(Val[0]))

	        # # Get "verg_gaze_coord_x"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"verg_gaze_coord_x: " + '{:.2f}'.format(Val[0]))

	        # # Get "verg_gaze_coord_y"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"verg_gaze_coord_y: " + '{:.2f}'.format(Val[0]))

	        # # Get "verg_gaze_coord_z"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"verg_gaze_coord_z: " + '{:.2f}'.format(Val[0]))

	        # # Get "hdtrk_X"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"hdtrk_X: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "hdtrk_Y"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"hdtrk_Y: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "hdtrk_Z"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"hdtrk_Z: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "hdtrk_az"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"hdtrk_az: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "hdtrk_el"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"hdtrk_el: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "hdtrk_rl"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"hdtrk_rl: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "ET3S_scene_number"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_SByte)
            # if (FlagData):
            #     print(f"ET3S_scene_number: " + '{:d}'.format(Val[0]))

	        # # Get "ET3S_gaze_length"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"ET3S_gaze_length: " + '{:.1f}'.format(Val[0]))

	        # # Get "ET3S_horz_gaze_coord"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"ET3S_horz_gaze_coord: " + '{:.1f}'.format(Val[0]))

	        # # Get "ET3S_vert_gaze_coord"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"ET3S_vert_gaze_coord: " + '{:.1f}'.format(Val[0]))

	        # # Get "eyeplot_x"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"eyeplot_x: " + '{:.1f}'.format(Val[0]))

	        # # Get "eyeplot_y"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     print(f"eyeplot_y: " + '{:.1f}'.format(Val[0]))

	        # # Get "eye_location_x"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"eye_location_x: " + '{:.2f}'.format(Val[0]*0.01) + '/{:.2f}'.format(ValR[0]*0.01))

	        # # Get "eye_location_y"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"eye_location_y: " + '{:.2f}'.format(Val[0]*0.01) + '/{:.2f}'.format(ValR[0]*0.01))

	        # # Get "eye_location_z"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"eye_location_z: " + '{:.2f}'.format(Val[0]*0.01) + '/{:.2f}'.format(ValR[0]*0.01))

	        # # Get "gaze_dir_x"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"gaze_dir_x: " + '{:.3f}'.format(Val[0]*0.001) + '/{:.3f}'.format(ValR[0]*0.001))

	        # # Get "gaze_dir_y"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"gaze_dir_y: " + '{:.3f}'.format(Val[0]*0.001) + '/{:.3f}'.format(ValR[0]*0.001))

	        # # Get "gaze_dir_z"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Int16)
            #     if (FlagDataR):
            #         print(f"gaze_dir_z: " + '{:.3f}'.format(Val[0]*0.001) + '/{:.3f}'.format(ValR[0]*0.001))

	        # # Get "aux_sensor_X"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"aux_sensor_X: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "aux_sensor_Y"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"aux_sensor_Y: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "aux_sensor_Z"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"aux_sensor_Z: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "aux_sensor_az"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"aux_sensor_az: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "aux_sensor_el"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"aux_sensor_el: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "aux_sensor_rl"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Int16)
            # if (FlagData):
            #     print(f"aux_sensor_rl: " + '{:.2f}'.format(Val[0]*0.01))

	        # # Get "eyelid_upper_vert"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_UInt16)
            #     if (FlagDataR):
            #         print(f"eyelid_upper_vert: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "eyelid_lower_vert"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_UInt16)
            #     if (FlagDataR):
            #         print(f"eyelid_lower_vert: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "blink_confidence"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt16)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_UInt16)
            #     if (FlagDataR):
            #         print(f"blink_confidence: " + '{:.1f}'.format(Val[0]) + '/{:.1f}'.format(ValR[0]))

	        # # Get "ellipse_angle"
            # FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_Single)
            # if (FlagData):
            #     FlagDataR, DIndex, FlagShift, ValR = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift - 1, TYPECODE_Single)
            #     if (FlagDataR):
            #         print(f"ellipse_angle: " + '{:.2f}'.format(Val[0]) + '/{:.2f}'.format(ValR[0]))

	        # Get "Gaze_LAOI"
            DIndex = 125
            FlagShift = 52
            print(DIndex)
            print(FlagShift)
            FlagData, DIndex, FlagShift, Val = ProcMsgDataItem(Buf, DIndex, CheckState, FlagShift, TYPECODE_UInt32)
            if (FlagData):
                print(f"Gaze_LAOI: " + '{:d}'.format(Val[0]))
                LAOIs = Val[0]
            # Return Buffer Array that has not been processed
            print("got the Gaze_LAOI")
            return Buf[(DataMsgSize + BIndex):], LAOIs

        # Return Buffer Array if not the whole eye data message received
        print("not the whole eye data message received")
        return Buf[BIndex:], None

    # Return empty array if there's no Argus Eye Data Message found
    print("there's no Argus Eye Data Message found")
    return Buf[len(Buf):], None


#------------------------------------------------------------------------------
# Main entry point for the Eye Tracker Sample Application
#    argv[1]    -   Eye Tracker Host IP Address
#    argv[2]    -   Eye Tracker Host IP Port Number
#    Return		-	None
#------------------------------------------------------------------------------
# # Get number of arguments
# NumArg = len(sys.argv)

# # Check whether it's correct
# if NumArg != 3:
#     # Show instruction message if number of arguments is not right
#     print("Please use command: py ETReceiveData.py IPAddress IPPort\n")

#     # Quit
#     sys.exit()

def ConnectET(IPAddress, PortNumber):
    global DataSocket, NetworkVersion, HostIPAddr, HostPortNum
    # Get Eye Tracker Host IP Address to connect
    # HostIPAddr = sys.argv[1]
    HostIPAddr = IPAddress

    # Get Eye Trackt Port Number to connect
    # HostPortNum = int(sys.argv[2])
    HostPortNum = PortNumber

    # Create TCP socket to connect to host
    CmdSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set TCP_NODELAY
    CmdSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # Set time out to 10 seconds
    CmdSocket.settimeout(10.0)

    # Show message for starting
    print(f"Start to connect {HostIPAddr} at port {HostPortNum}...\n")

    # Initialize default Argus Network Version to Protocol Version 0
    NetworkVersion = 0

    # Initialize Network Connected Flag
    FlagConnected = True

    # Try to connect to Eye Tracker Host
    try:
        # Connect to host
        CmdSocket.connect((HostIPAddr, HostPortNum))

    # Failed
    except Exception as e:
        # Change Connection Flag to False if failed
        FlagConnected = False

    # Send command to get Argus Network Protocol Version if connected
    if (FlagConnected):
        FlagConnected = SendETCmd(CmdSocket, CMD_GET_VERSION, 0)

    # Try to get Network Protocol Version
    if (FlagConnected):
        try:
            # Receive response
            CmdRcvBuf = CmdSocket.recv(MSG_BUFFER_SIZE)

            # Make sure it's valid
            if (len(CmdRcvBuf) > 16):
                # Calculate Check Sum of response
                CSum = CalCheckSum(CmdRcvBuf, len(CmdRcvBuf))

                # Check whether it's Network Protocol Version
                if (CSum == 0) & (GetBufDWord(CmdRcvBuf, 0) == MSG_ARGUS_SIGNATURE) & (GetBufWord(CmdRcvBuf, 8) == CMD_GET_VERSION):
                    # Update Network Protocol Version
                    NetworkVersion = CmdRcvBuf[16]
        except Exception as e:
            # Use Network Protocol Version 0 if failed
            NetworkVersion = 0

    # Create TCP socket to receive data from host if connected
    if (FlagConnected):
        DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Send Command to Host to wait for "Send Data" TCP connection if connected
    if (FlagConnected):
        FlagConnected = SendETCmd(CmdSocket, CMD_SET_CONNECT_TYPE, SOCKET_TYPE_SDATA_TCP)

    # Build "Send Data" TCP connection if connected
    if (FlagConnected):
        try:
            # Connect Data Socket to Host to build "Send Data" TCP connection
            DataSocket.connect((HostIPAddr, HostPortNum))

            # Set Data Socket time out to 10ms if succeeded
            DataSocket.settimeout(0.01)
        except Exception as e: 
            # Change Connection Flag to False if failed
            FlagConnected = False

    # Quit if failed to build the connection
    if (FlagConnected == False):
        # Show message
        print(f"Failed to connect {HostIPAddr} at port {HostPortNum}!")
        print("Please double check the IP Address and Port Number that Eye Tracker is listening!\n")
        
        # Quit
        sys.exit()

    # Show message for starting
    print(f"Start to receive eye data from {HostIPAddr}... (Press ESC to quit!)\n")
    LAOIs = GetETData(FlagConnected)
    return LAOIs

# Received eye data from host if connected
def GetETData(FlagConnected):
    LAOIs = 0
    # Initialize Data Receive Buffer
    
    if (FlagConnected):
        # Quit if ESC Key is pressed
        if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
            sys.exit()

        # Try to receive data frome host
        try:
            DataRcvBuf = bytearray()
            # Receive data
            RBuf = DataSocket.recv(MSG_BUFFER_SIZE - len(DataRcvBuf))
                
            # Check whether it lost connection
            if (len(RBuf) > 0):

                # Get data
                DataRcvBuf += RBuf

                # Make sure there're enough data to start processing
                if (len(DataRcvBuf) > MSG_HEADER_SIZE):

                    # Processing eye data based on Network Protocol Version
                    if (NetworkVersion > 0):
                        # Network Porotocol Version 1
                        DataRcvBuf, LAOIs = ProcMsgDataV1(DataRcvBuf)
                        print("Received LAOIs from ProcMsgDataV1", LAOIs)
                        requests.post("http://localhost:100/attentionstate", json={"LAOIs": LAOIs})
            else:
                # Set Flag to Not Connected if lost connection
                FlagConnected = False

        # Continue if Timeout
        except socket.timeout as e:
            print("socket timeout")
            pass

        # Set Flag to Not Connected if failed
        except Exception as e: 
            print("socket connection failed", e)
            FlagConnected = False
    else:
        # Show message
        print(f"Failed to receive data from {HostIPAddr} at port {HostPortNum}! Please double check the connection!")
        return  None
# # Quit
# sys.exit()
if __name__ == "__main__":
    #------------------------------------------------------------------------------
    # Main entry point for the Eye Tracker Sample Application
    #    argv[1]    -   Eye Tracker Host IP Address
    #    argv[2]    -   Eye Tracker Host IP Port Number
    #    Return		-	None
    #------------------------------------------------------------------------------
    # Get number of arguments
    NumArg = len(sys.argv)

    # Check whether it's correct
    if NumArg != 3:
        # Show instruction message if number of arguments is not right
        print("Please use command: py ETReceiveData.py IPAddress IPPort\n")

        # Quit
        sys.exit()

    # Get Eye Tracker Host IP Address to connect
    HostIPAddr = sys.argv[1]

    # Get Eye Trackt Port Number to connect
    HostPortNum = int(sys.argv[2])
    print("Starting ETReceiveLAOI")
    while True:
        ConnectET(HostIPAddr, HostPortNum)

