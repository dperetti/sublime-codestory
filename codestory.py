import sublime
import sublime_plugin
import os
import re
import subprocess

from .codestory_settings import settings  # #jzMgj#


CODE_STORY_REGION_KEY = 'CodeStoryTokenRegion'


class CodeStoryToggleSettingsCommand(sublime_plugin.ApplicationCommand):  # #EDrHt#

    """Enables/Disables settings"""

    def run(self, setting):
        # toggle and save to disk
        settings.set(setting, not settings.get(setting))
        settings.save_settings()


class CodeStoryListener(sublime_plugin.EventListener):
    regions = []
    view = None

    def on_activated(self, view):  # #RJ29g#
        self.adjust_highlight(view)

    def on_modified_async(self, view):
        self.adjust_highlight(view)

    def on_post_window_command(self, window, command, args):
        if command == "code_story_toggle_settings":
            for window in sublime.windows():
                for view in window.views():
                    self.adjust_highlight(view)

    def on_hover(self, view, point, hover_zone):  # #HTMUp#
        """
        Called when the user's mouse hovers over a view for a short period.
        Shows a popup with a "View in Code Story" link.
        """
        # check if we're over one of the highlighted regions
        for r in self.regions:
            if r.contains(point):
                documentation_path = get_documentation_path(view)
                if documentation_path is False:
                    view.show_popup('No Code Story Documentation can be found',
                                    sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 400, 400)
                else:
                    # save the view because we'll need it in self.on_navigate()
                    self.view = view
                    token = view.substr(r)  # the string of the token
                    view.show_popup('<a href="' + token + '" style="text-decoration: none">View in Code Story</a>',
                                    sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 400, 400, self.on_navigate)

    def on_navigate(self, href):  # #pGVgd#
        """
        Called when the user click the "View in Code Story" link.

        """
        # remove the hash at the beginining and and of the token
        token = href[1:-1]
        # get the path of the documentation
        documentation_path = get_documentation_path(self.view)
        if documentation_path is False:
            sublime.error_message("No Code Story Documentation can be found")
            return
        cmd = [settings.codestory_binary_path, '-p', documentation_path, '-s', token]
        try:
            subprocess.Popen(cmd, shell=False)
        except Exception as e:
            sublime.error_message(str(e))

    def adjust_highlight(self, view):  # #Dk2sT#
        if settings.get('enable_highlighting'):
            self.highlight(view)
        else:
            self.clear_highlight(view)

    def highlight(self, view):  # #T5G9e#
        """
        Create Sublime regions for Code Story tokens.
        """
        # find regions that look like a Code Story token. Ex: #AB32F#
        self.regions = view.find_all(r'#[abcdefghijklmonpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890]{5}#')
        # mark those regions
        # http://www.sublimetext.com/docs/3/api_reference.html#sublime.View
        view.add_regions(CODE_STORY_REGION_KEY, self.regions, 'comment', 'dot', sublime.DRAW_EMPTY)

    def clear_highlight(self, view):
        """
        Clear all highlighted regions
        """
        view.erase_regions(CODE_STORY_REGION_KEY)


def find_up_documentation(file):
    """
    Traverse up the hierarchy in order to find a Code Story documentation,
    starting from the folder of the specified file.
    """
    folder = file  # not really, but see below
    try:
        while folder != '/':
            folder = os.path.dirname(folder)
            for f in os.listdir(folder):
                if re.match('.+\.codestory$', f):
                    return os.path.join(folder, f)
    except Exception as e:
        sublime.error_message(str(e))
    return False


def get_documentation_path(view):
    """
    Try to find the Code Story documentation of the project.
    It is first looked up in the project's settings, then in the User settings (not a great
    place for btw).
    If nothing is set in the settings, try to find one upwards in the hierarchy, starting from the current file.
    """
    # defined relatively to the project
    documentation_path = view.settings().get('code_story_documentation_path')
    if documentation_path:
        documentation_path = os.path.join(view.window().extract_variables()['project_path'], documentation_path)
    else:
        documentation_path = find_up_documentation(view.window().extract_variables()['file'])

    return documentation_path
