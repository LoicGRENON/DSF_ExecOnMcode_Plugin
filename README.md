# DSF_ExecOnMcode_Plugin

This branch supports **DuetWebControl / DuetSoftwareFramework 3.7**.
See [MIGRATION-3.7.md](MIGRATION-3.7.md) for API changes, build/test instructions
and the scope of hardware validation.

![ExecOnMcode](https://user-images.githubusercontent.com/974748/212554271-af1bf32e-a8fa-4a3b-988b-4c76a5a31052.png)

## Description
ExecOnMcode is a SBC plugin for [DuetSoftwareFramework](https://github.com/Duet3D/DuetSoftwareFramework) and based on [dsf-python](https://github.com/Duet3D/dsf-python) to run commands on user-defined M-Codes.

This plugin is based on the original idea from [wilriker's execonmcode](https://github.com/wilriker/execonmcode).

It provides M1200 M-Code which is used to update the interception filters.

Others M-Codes and related commands can be added by editing the `ExecOnMcode.json` file located in System directory and then issuing `M1200` (or restarting the plugin) to update the interception filters.

Command arguments can be passed from G-Code parameters, e.g: when issuing `Mxxx "arg1 arg2"`, the parameters `arg1 arg2` will be appended as arguments to the command triggered by `Mxxx`.

## Installation

1. Open the **Plugins** page in Duet Web Control 3.7.
2. Select **Install plugin**, choose the plugin ZIP and follow the installation steps.
3. Start the plugin. Open **ExecOnMcode** under **Preferences** to edit commands.

Configuration is stored at `0:/sys/ExecOnMcode/ExecOnMcode.json`. Opening the
panel only reads it; saving uploads the file and sends `M1200` to reload filters.

## Limitations

As the plugin runs under *dsf* user on the system, the command you wish to run using *ExecOnMcode* should be allowed to be run from that user.

If for some reason you want to go beyond that limitation, create a `010_dsf-nopasswd` file into `/etc/sudoers.d/` with the following content : `dsf ALL=(ALL) NOPASSWD: ALL`
<br>Then use `sudo` with the command you wish to run using *ExecOnMcode*.
