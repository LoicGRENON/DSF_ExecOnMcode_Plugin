<template>
    <v-card style="overflow-x: hidden;" class="pa-0 ma-0">
        <v-card-text>
            <v-data-table :headers="CmdTableHeaders" :items="cmds_list" :items-per-page="10" item-key="cmd_id" sort-by="cmd_id" class="pa-0 ma-0">
                <template v-slot:top>
                    <v-toolbar dense dark class="elevation-0" color="transparent">
                        <v-toolbar-title class="blue--text"><v-icon color="light-blue darken-1" large>mdi-powershell</v-icon> SBC commands</v-toolbar-title>
                        <v-spacer></v-spacer>
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
                                                    <v-text-field v-bind="attrs" v-on="on" label="M-Code*" required v-model="editItem.cmd_id"></v-text-field>
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
                                                    <v-text-field v-bind="attrs" v-on="on" label="Command to execute on SBC*" required v-model="editItem.cmd_value"></v-text-field>
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
                                        <v-col cols="6" class="ma-0 pa-0">
                                            <v-tooltip bottom>
                                                <template v-slot:activator="{ on, attrs }">
                                                    <span v-bind="attrs" v-on="on"><v-switch label="Enabled" v-model="editItem.cmd_enabled"></v-switch></span>
                                                </template>
                                                <span>Toggle to disable or enable the command</span>
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
                <template v-slot:item.actions="{ item }">
                    <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="mr-2" v-bind="attrs" v-on="on" @click="edit_cmd(item)">mdi-pencil</v-icon>
                        </template>
                        <span>Edit command</span>
                    </v-tooltip>
                    <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="mr-2" v-bind="attrs" v-on="on" @click="del_cmd(item.cmd_id)">mdi-delete</v-icon>
                        </template>
                        <span>Delete command</span>
                    </v-tooltip>
                </template>
            </v-data-table>
        </v-card-text>
    </v-card>
</template>

<script>
    export default {
        data: function () {
            return {
                alert_required_value: false,
                edit_cmd_dialog: false,
                confirmDelEvents: false,
                deleteItem: null,
                is_newCmd: false,  // False: command being edited | True: new command to add
                editItem: {
                    cmd_id: null,
                    cmd_name: "Enter name",
                    cmd_value: "Enter command to execute on SBC",
                    cmd_enabled: false,
                    cmd_timeout: 30
                },
                last_cmd_id: 1201,
                current_cmd_id: null,
                cmds_list: [  // TODO: Read cmds_list from the JSON file using a GET request when opening the tab
                    {
                        cmd_id: 1201,
                        cmd_name: "Echo Test",
                        cmd_value: "echo 'If you can see this, it means ExecOnMcode is working !'",
                        cmd_enabled: true,
                        cmd_timeout: 30
                    },
                ],
                CmdTableHeaders: [
                    { text: 'M-Code', value: 'cmd_id' },
                    { text: 'Name', value: 'cmd_name' },
                    { text: 'Command', value: 'cmd_value' },
                    { text: 'Enabled', value: 'cmd_enabled' },
                    { text: 'Timeout', value: 'cmd_timeout' },
                    { text: 'Actions', value: 'actions', sortable: false },
                ]
            }
        },
        methods: {
            async sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            },
            async validateData() {
                var bData_ok = true;
                if(!this.editItem.cmd_name){
                    bData_ok = false;
                }else if(!this.editItem.cmd_value){
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
                    // TODO: save data using POST request
                    if(this.is_newCmd){
                        this.cmds_list.push(this.editItem);
                        this.last_cmd_id = this.current_cmd_id;
                    }
                    this.edit_cmd_dialog = false;
                    return;
                }
            },
            new_cmd(){
                this.current_cmd_id = this.last_cmd_id + 1;
                var new_command ={
                    cmd_id: this.current_cmd_id,
                    cmd_name: "",
                    cmd_value: "",
                    cmd_enabled: true,
                    cmd_timeout: 30
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
                var requiredIndex = this.cmds_list.findIndex(el => el.cmd_id == this.deleteItem);
                if(requiredIndex === -1){
                    return false;
                }
                this.cmds_list.splice(requiredIndex, 1);
                this.deleteItem = null;
            },
		},
    }
</script>