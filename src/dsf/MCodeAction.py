class MCodeAction:
    def __init__(self, action):
        if 'cmd_code' not in action:
            raise KeyError('code must be provided in plugin.json')
        if 'cmd_command' not in action:
            raise KeyError('command must be provided in plugin.json')
        self.cmd_code = action['cmd_code']
        self.cmd_command = action['cmd_command']

        try:
            self.cmd_name = action['cmd_name']
        except KeyError:
            self.cmd_name = ''

        try:
            self.cmd_timeout = int(action['cmd_timeout'])
            if self.cmd_timeout == 0:
                self.cmd_timeout = None
        except KeyError:
            self.cmd_timeout = 30

        try:
            self.cmd_capture_output = bool(action['cmd_capture_output'])
        except KeyError:
            self.cmd_capture_output = False

        try:
            self.cmd_user = action['cmd_user']
            # TODO: Check if the user actually exists on the system
        except KeyError:
            self.cmd_user = "dsf"

        try:
            self.cmd_enabled = action['cmd_enabled']
        except KeyError:
            self.cmd_enabled = True

        self.__sanitize_code()

    def __sanitize_code(self):
        # TODO
        pass
