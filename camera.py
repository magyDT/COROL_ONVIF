from onvif import ONVIFCamera
from time import sleep


long_line = ""
for i in range(80):
    long_line += "-"


class Camera:
    def __init__(self, ip, port, login, password):
        # Connecting to the camera
        self.my_cam = ONVIFCamera(
            ip,
            port,
            login,
            password
        )

        # Creating media service
        self.media_service = self.my_cam.create_media_service()

        # Edited "site-packages/zeep/xsd/types/simple.py"
        #     def pythonvalue(self, xmlvalue):
        #         return xmlvalue

        # Getting profiles
        self.profiles = self.media_service.GetProfiles()
        self.media_profile = self.profiles[0]

        # Creating PTZ service
        self.ptz = self.my_cam.create_ptz_service()

        # Getting ptz move options
        self.request_absolute_move = self.ptz.create_type("AbsoluteMove")
        self.request_absolute_move.ProfileToken = self.media_profile.token

        self.request_stop = self.ptz.create_type("Stop")
        self.request_stop.ProfileToken = self.media_profile.token

        # Creating imaging service
        self.imaging = self.my_cam.create_imaging_service()

        # Getting imaging move options
        self.request_focus_change = self.imaging.create_type("Move")
        self.request_focus_change.VideoSourceToken = self.media_profile.VideoSourceConfiguration.SourceToken
        
        self.stop()

    # Get position of the camera
    def get_ptz_position(self):
        # Getting PTZ status
        status = self.ptz.GetStatus({"ProfileToken": self.media_profile.token})

        print(long_line)
        print("PTZ position: " + str(status.Position))
        print(long_line)

    def get_focus_options(self):
        # Getting imaging status
        imaging_status = self.imaging.GetStatus({"VideoSourceToken": self.media_profile.VideoSourceConfiguration.SourceToken})

        print(long_line)
        # Getting available imaging services
        request = self.imaging.create_type("GetServiceCapabilities")
        imaging_service_capabilities = self.ptz.GetServiceCapabilities(request)

        print("Service capabilities: " + str(imaging_service_capabilities))
        print(long_line)
        print("Imaging status: " + str(imaging_status))
        print(long_line)

    # Stop any movement
    def stop(self):
        self.request_stop.PanTilt = True
        self.request_stop.Zoom = True

        self.ptz.Stop(self.request_stop)


    # Absolute move functions
    def perform_absolute_move(self):
        # Start absolute move
        self.ptz.AbsoluteMove(self.request_absolute_move)

        sleep(4)

    def move_absolute(self, x, y, zoom):
        print("Moving to: \"" +
              str(x) + ":" + str(y) + ":" + str(zoom) +
              "\""
              )

        status = self.ptz.GetStatus({"ProfileToken": self.media_profile.token})
        status.Position.PanTilt.x = x
        status.Position.PanTilt.y = y
        status.Position.Zoom.x = zoom

        self.request_absolute_move.Position = status.Position

        self.perform_absolute_move()

    # Focus change functions
    def change_focus(self, speed, timeout):
        print("Changing focus with speed: \"" +
              str(speed) +
              "\" and timeout: \"" +
              str(timeout) +
              "\""
              )

        self.request_focus_change.Focus = {
            "Continuous": {
                "Speed": speed
            }
        }

        self.imaging.Move(self.request_focus_change)

        sleep(timeout)

        self.stop()

        sleep(2)
