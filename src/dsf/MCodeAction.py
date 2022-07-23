# -*- coding: utf-8 -*-

class MCodeAction:
    def __init__(self, action):
        if 'code' not in action:
            raise KeyError('code must be provided in plugin.json')
        if 'command' not in action:
            raise KeyError('command must be provided in plugin.json')
        self.code = action['code']
        self.cmd = action['command']

        try:
            self.timeout = int(action['timeout'])
            if self.timeout == 0:
                self.timeout = None
        except KeyError:
            self.timeout = 30

        try:
            self.flush = action['flush']
        except KeyError:
            self.flush = False

        try:
            self.capture_output = action['capture_output']
        except KeyError:
            self.capture_output = False

        try:
            self.user = action['user']
        except KeyError:
            self.user = "dsf"

        self.__sanitize_code()

    def __sanitize_code(self):
        # TODO
        pass
