<template>
    <v-card style="overflow-x: hidden;" class="pa-0 ma-0">
        <v-card-text>
            <v-data-table :headers="CmdTableHeaders" :items="cmds_list" :items-per-page="10" item-key="cmd_code" sort-by="cmd_code" class="pa-0 ma-0">
                <template v-slot:top>
                    <v-toolbar dense dark class="elevation-0" color="transparent">
                        <v-toolbar-title class="blue--text"><v-icon color="light-blue darken-1" large>mdi-powershell</v-icon> SBC commands</v-toolbar-title>
                        <v-spacer></v-spacer>
                        <v-btn icon @click="reload_cmds()"><v-icon color="light-blue darken-1" large>mdi-reload</v-icon></v-btn>
                        <v-tooltip top>
                            <template v-slot:activator="{ on, attrs }">
                                <v-btn icon v-bind="attrs" v-on="on" @click="new_cmd()"><v-icon color="light-blue darken-1" large>mdi-plus-box</v-icon></v-btn>
                            </template>
                            <span>Add new command</span>
                        </v-tooltip>
                        <v-dialog v-model="edit_cmd_dialog" persistent max-width="700px">
                            <v-card>
                                <v-card-title>
                                    <v-toolbar dense dark class="info">
                                        <v-toolbar-title v-if="is_newCmd">New command</v-toolbar-title>
                                        <v-toolbar-title v-else>Edit command</v-toolbar-title>
                                        <v-spacer></v-spacer>
                                        <v-btn icon @click="edit_cmd_dialog=false"><v-icon large>mdi-close-box</v-icon></v-btn>
                                        <v-btn icon @click="validateData()"><v-icon large>mdi-check</v-icon></v-btn>
                                    </v-toolbar>
                                    <v-alert style="position: absolute; z-index:99999;" :value="alert_required_value" type="error" transition="scale-transition">Required values have not been entered !</v-alert>
                                </v-card-title>
                                <v-card-text>
                                    <v-row dense class="mx-2">
                                        <v-col cols="12" class="ma-0 pa-0">
                                            <v-tooltip bottom>
                                                <template v-slot:activator="{ on, attrs }">
                                                    <v-text-field v-bind="attrs" v-on="on" label="M-Code*" required v-model="editItem.cmd_code"></v-text-field>
                                                </template>
                                                <span>Enter the M-Code to trigger the command</span>
                                            </v-tooltip>
                                        </v-col>
                                    </v-row>
                                    <v-row dense class="mx-2 my-n4">
                                        <v-col cols="12" class="ma-0 pa-0">
                                            <v-tooltip bottom>
                                                <template v-slot:activator="{ on, attrs }">
                                                    <v-text-field v-bind="attrs" v-on="on" label="Name*" required v-model="editItem.cmd_name"></v-text-field>
                                                </template>
                                                <span>Enter a friendly name for the command</span>
                                            </v-tooltip>
                                        </v-col>
                                    </v-row>
                                    <v-row dense class="mx-2 my-n4">
                                        <v-col cols="12" class="ma-0 pa-0">
                                            <v-tooltip bottom>
                                                <template v-slot:activator="{ on, attrs }">
                                                    <v-text-field v-bind="attrs" v-on="on" label="Command to execute on SBC*" required v-model="editItem.cmd_command"></v-text-field>
                                                </template>
                                                <span>Enter command to execute on SBC</span>
                                            </v-tooltip>
                                        </v-col>
                                    </v-row>
                                    <v-row dense class="mx-2 my-n4">
                                        <v-col cols="12" class="ma-0 pa-0">
                                            <v-tooltip bottom>
                                                <template v-slot:activator="{ on, attrs }">
                                                    <v-text-field v-bind="attrs" v-on="on" label="Timeout*" number required v-model="editItem.cmd_timeout"></v-text-field>
                                                </template>
                                                <span>Timeout in seconds</span>
                                            </v-tooltip>
                                        </v-col>
                                    </v-row>
                                    <v-row dense class="mx-2 my-n4">
                                        <v-col class="ma-0 pa-0">
                                            <v-tooltip bottom>
                                                <template v-slot:activator="{ on, attrs }">
                                                    <span v-bind="attrs" v-on="on"><v-switch label="Enabled" v-model="editItem.cmd_enabled"></v-switch></span>
                                                </template>
                                                <span>Toggle to disable or enable the command</span>
                                            </v-tooltip>
                                        </v-col>
                                        <v-col class="ma-0 pa-0">
                                            <v-tooltip bottom>
                                                <template v-slot:activator="{ on, attrs }">
                                                    <span v-bind="attrs" v-on="on"><v-switch label="Hide output" v-model="editItem.cmd_capture_output"></v-switch></span>
                                                </template>
                                                <span>Hide the command output from the DWC console</span>
                                            </v-tooltip>
                                        </v-col>
                                    </v-row>
                                    <v-row dense class="mx-2 my-n4">
                                        <v-col cols="12">
                                            <small>*indicates required field</small>
                                        </v-col>
                                    </v-row>
                                </v-card-text>
                                <v-card-actions>
                                    <v-spacer></v-spacer>
                                    <v-btn color="blue darken-1" text @click="edit_cmd_dialog=false">Close</v-btn>
                                    <v-btn color="blue darken-1" text @click="validateData()">Save</v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-dialog>
                        <confirm-dialog :shown.sync="confirmDelEvents" title="Confirm delete" prompt="Delete command ?" @confirmed="confirm_del_cmd()"></confirm-dialog>
                    </v-toolbar>
                </template>
                <template v-slot:item.cmd_enabled="{ item }">
                    <v-icon color="red darken-1" v-if="!item.cmd_enabled">mdi-close-circle</v-icon>
                    <v-icon color="light-green darken-1" v-else>mdi-checkbox-marked-circle</v-icon>
                </template>
                <template v-slot:item.actions="{ item }">
                    <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="mr-2" v-bind="attrs" v-on="on" @click="edit_cmd(item)">mdi-pencil</v-icon>
                        </template>
                        <span>Edit command</span>
                    </v-tooltip>
                    <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="mr-2" v-bind="attrs" v-on="on" @click="del_cmd(item.cmd_code)">mdi-delete</v-icon>
                        </template>
                        <span>Delete command</span>
                    </v-tooltip>
                </template>
            </v-data-table>
        </v-card-text>
    </v-card>
</template>

<script>

    import { mapGetters, mapActions } from 'vuex'

    export default {
        computed: {
            ...mapGetters('machine', ['connector'])  // map DWC connector to make HTTP requests
        },
        data: function () {
            return {
                alert_required_value: false,
                edit_cmd_dialog: false,
                confirmDelEvents: false,
                deleteItem: null,
                is_newCmd: false,  // False: command being edited | True: new command to add
                editItem: {
                    cmd_code: null,
                    cmd_name: "Enter a name",
                    cmd_command: "Enter a command to execute on SBC",
                    cmd_enabled: false,
                    cmd_timeout: 30,
                    cmd_capture_output: false
                },
                cmds_list: [],
                CmdTableHeaders: [
                    { text: 'M-Code', value: 'cmd_code' },
                    { text: 'Name', value: 'cmd_name' },
                    { text: 'Command', value: 'cmd_command' },
                    { text: 'Enabled', value: 'cmd_enabled' },
                    { text: 'Timeout', value: 'cmd_timeout' },
                    { text: 'Actions', value: 'actions', sortable: false },
                ]
            }
        },
        created () {
            this.reload_cmds();  // reload the commands list when the panel is opened
        },
        methods: {
            ...mapActions('machine', ['request']),  // Map the request method of the DWC connector
            async sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            },
            async validateData() {
                var bData_ok = true;
                if(!this.editItem.cmd_name){
                    bData_ok = false;
                }else if(!this.editItem.cmd_command){
                    bData_ok = false;
                }else if(this.editItem.cmd_timeout < 1){
                    bData_ok = false;
                }

                if(!bData_ok){
                    this.alert_required_value = true;
                    await this.sleep(2000);
                    this.alert_required_value = false;
                    return;
                }else {
                    if(this.is_newCmd){
                        this.cmds_list.push(this.editItem);
                    }
                    this.save_cmds()
                    this.edit_cmd_dialog = false;
                    return;
                }
            },
            get_next_available_code(){
                // Return the next available code, starting from M1201
                var next_available_code = 1201;
                this.cmds_list.forEach((item) => {
                    console.log(item);
                    if(item.cmd_code != "M".concat(next_available_code))
                        return next_available_code;
                    next_available_code++;
                });
                return next_available_code;
            },
            new_cmd(){
                var new_command ={
                    cmd_code: "M" + this.get_next_available_code(),
                    cmd_name: "",
                    cmd_command: "",
                    cmd_enabled: true,
                    cmd_timeout: 30,
                    cmd_capture_output: false
                }
                this.edit_cmd(new_command, true);
            },
            edit_cmd(eventItem, is_newCmd=false){
                this.is_newCmd = is_newCmd;
                this.editItem = eventItem;
                this.edit_cmd_dialog = true;
            },
            del_cmd(eventItem){
                this.deleteItem = eventItem;
                this.confirmDelEvents = true;
            },
            confirm_del_cmd(){
                var requiredIndex = this.cmds_list.findIndex(el => el.cmd_code == this.deleteItem);
                if(requiredIndex === -1){
                    return false;
                }
                this.cmds_list.splice(requiredIndex, 1);
                this.deleteItem = null;
                this.save_cmds()
            },
            async reload_cmds(){
                const response = await this.connector.request('GET', 'machine/ExecOnMcode/getCmdList', null, 'json');
                this.cmds_list = response.data;
            },
            async save_cmds(){
                const payload = new Blob([JSON.stringify(this.cmds_list)]);
                await this.connector.request('POST', 'machine/ExecOnMcode/saveCmdList', null, 'json', payload);
            },
		},
    }
</script>