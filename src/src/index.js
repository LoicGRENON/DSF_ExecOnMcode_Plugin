'use strict'

import { registerRoute } from '@/routes'
import ExecOnMcode from './ExecOnMcode.vue'
// Register a route via Settings -> ExecOnMcode
registerRoute(ExecOnMcode, {
	Settings: {
		ExecOnMcode: {
			icon: 'mdi-powershell',
			caption: 'ExecOnMcode',
			path: '/ExecOnMcode'
		}
	}
});