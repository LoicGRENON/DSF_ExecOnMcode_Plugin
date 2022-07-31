'use strict'

import { registerSettingTab } from '../../routes'

import ExecOnMcode from './ExecOnMcode.vue'
// Register a setting tab on the Machine-specific settings page
registerSettingTab(false, 'settings-machine-ExecOnMcode', ExecOnMcode, 'ExecOnMcode');