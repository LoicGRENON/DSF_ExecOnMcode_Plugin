# DSF_ExecOnMcode_Plugin

## Description
ExecOnMcode is a SBC plugin for DuetSoftwareFramework (based on dsf-python) to run commands on user-defined M-Codes.

It provides two default M-Codes:

- M1200 which is used to update the interception filters
- M7722 to shutdown the SBC after 1 minute delay

Others M-Codes and related commands can be added by editing the `filters.json` file and then issuing `M1200` (or restarting the plugin) to update the interception filters.

## Installation

As this plugin requires Super-User rights, it requires additional steps to be installed as defined at https://github.com/Duet3D/DuetSoftwareFramework/wiki/Third-Party-Plugins#root-plugins

`RootPluginSupport` can be enabled by the following command:  
`sudo sed -ie 's|"RootPluginSupport": .*,|"RootPluginSupport": true,|g' /opt/dsf/conf/config.json`  
DCS must be restarted either using a system reboot or via `sudo systemctl restart duetcontrolserver`

Once `RootPluginSupport` has been enabled, go on the `System` Tab of Duet Web Control, click on "Upload System Files" and select the plugin zip archive.  
Follow the on-screen instructions to install the plugin.
