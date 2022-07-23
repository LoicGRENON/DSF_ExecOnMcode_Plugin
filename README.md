# DSF_ExecOnMcode_Plugin

## Description
ExecOnMcode is a SBC plugin for DuetSoftwareFramework (based on dsf-python) to run commands on user-defined M-Codes.

It provides M1200 M-Code which is used to update the interception filters.

Others M-Codes and related commands can be added by editing the `filters.json` file and then issuing `M1200` (or restarting the plugin) to update the interception filters.

## Installation

Go on the `Plugins` Tab of Duet Web Control, select `External plugins`, click on "Upload System Files" and select the plugin zip archive.  
Follow the on-screen instructions to install the plugin.
