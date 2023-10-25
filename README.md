# ASTERISK_API_CAM_save TCP server + client
Server connect to cameras and wait request from client by socker TCP where he takes json.
json example: 
{
  'cam': 3, 
  'data': '2023-12-12_00-00'
}
After connected, server saves screenshot from camera.
