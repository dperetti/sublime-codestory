import sublime


class CodeStorySettings:

    def __init__(self):  # #pADQS#
        self._settings = None
        self._codestory_binary_path_error_shown = False
        self.codestory_binary_path = None

    def get(self, key, default=None):
        if self._settings is None or not self._settings.has(key):
            self.load_settings()
        return self._settings.get(key, default)

    def set(self, key, value):  # #FThat#
        if self._settings is None:
            self.load_settings()
        return self._settings.set(key, value)

    def load_settings(self):  # #fsnGh#
        # load Code Story settings
        self._settings = sublime.load_settings('Code Story.sublime-settings')

        # the path of Code Story app binary
        codestory_binary_setting = self._settings.get("codestory_binary_path")
        # codestory_binary_setting can be either the path of the binary or
        # a platform based dict(osx=<path>,windows=<path>,linux=<path>)
        if isinstance(codestory_binary_setting, dict):
            self.codestory_binary_path = codestory_binary_setting.get(sublime.platform())
            if not self.codestory_binary_path:
                self.codestory_binary_path = codestory_binary_setting.get('default')
        else:
            self.codestory_binary_path = codestory_binary_setting

    def save_settings(self):
        """ Save settings to disk """
        self._settings = sublime.save_settings('Code Story.sublime-settings')


if 'settings' not in globals():
    settings = CodeStorySettings()  # #mLEkE#
