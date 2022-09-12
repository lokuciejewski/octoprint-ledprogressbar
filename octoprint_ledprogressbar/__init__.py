# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin as plugin
import logging
import smbus2
from octoprint.events import Events

class Colour:
    red: int
    green: int
    blue: int

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue


class LEDProgressBar:

    def __init__(self):
        self.bus = smbus2.SMBus(1)
        self.device_address = 0x69

    def set_progress(self, percentage: float, colour: Colour):
        self._logger.info(
            f"Sending percentage {percentage} with colour RGB({colour.red}, {colour.green}, {colour.blue})")
        self.bus.write_i2c_block_data(self.device_address, 0, int(
            percentage), colour.red, colour.green, colour.blue)


class LEDProgressBarPlugin(plugin.StartupPlugin, plugin.SettingsPlugin,
                           plugin.AssetPlugin,
                           plugin.TemplatePlugin):

    def __init__(self, *args, **kwargs):
        self.p_bar = LEDProgressBar()

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "ledprogressbar": {
                "displayName": "Ledprogressbar Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "grododzierzca",
                "repo": "OctoPrint-LEDProgressBar",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/grododzierzca/OctoPrint-LEDProgressBar/archive/{target_version}.zip",
            }
        }
    
     # ~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    # ~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/ledprogressbar.js"],
            "css": ["css/ledprogressbar.css"],
            "less": ["less/ledprogressbar.less"]
        }

    def on_after_startup(self):
        self._logger.info("LED Progress Bar loaded!")

    def on_event(self, event, payload):
        if event == Events.PRINT_STARTED:
            self._logger.info("Print started")
            self.p_bar.set_progress(0, Colour(0, 10, 0))

        elif event == Events.PRINT_DONE:
            self._logger.info("Print completed")
            self.p_bar.set_progress(100, Colour(0, 10, 10)) 

    def on_print_progress(self, storage, path, progress):
        self.p_bar.set_progress(progress, Colour(0, 10, 0))




__plugin_name__ = "LED ProgressBar"
__plugin_version__ = "1.0.0"
__plugin_description__ = "LED Progress Bar module for OctoPrint"
__plugin_pythoncompat__ = ">=3.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = LEDProgressBarPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
