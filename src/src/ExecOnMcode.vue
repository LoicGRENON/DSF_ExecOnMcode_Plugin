<template>
    <v-card>
        <v-toolbar color="transparent" density="compact">
            <v-toolbar-title><v-icon color="light-blue-darken-1">mdi-powershell</v-icon> SBC commands</v-toolbar-title>
            <v-spacer />
            <v-btn icon="mdi-reload" aria-label="Reload commands" :disabled="loading || saving" @click="reloadCommands" />
            <v-btn icon="mdi-plus-box" aria-label="Add command" :disabled="loading || saving || !machine.isConnected" @click="newCommand" />
        </v-toolbar>
        <v-alert v-if="error" type="error" class="ma-4">{{ error }}</v-alert>
        <v-data-table :headers="headers" :items="commands" :loading="loading" :items-per-page="10"
                      item-value="cmd_code" :sort-by="[{ key: 'cmd_code', order: 'asc' }]">
            <template #item.cmd_enabled="{ item }">
                <v-icon :color="item.cmd_enabled ? 'light-green-darken-1' : 'red-darken-1'"
                        :aria-label="item.cmd_enabled ? 'Enabled' : 'Disabled'">
                    {{ item.cmd_enabled ? 'mdi-checkbox-marked-circle' : 'mdi-close-circle' }}
                </v-icon>
            </template>
            <template #item.actions="{ item }">
                <v-btn icon="mdi-pencil" variant="text" size="small" :aria-label="`Edit ${item.cmd_code}`"
                       :disabled="saving" @click="editCommand(item)" />
                <v-btn icon="mdi-delete" variant="text" size="small" :aria-label="`Delete ${item.cmd_code}`"
                       :disabled="saving" @click="deleteCode = item.cmd_code; confirmDelete = true" />
            </template>
        </v-data-table>
        <v-dialog v-model="editDialog" persistent max-width="700">
            <v-card>
                <v-form @submit.prevent="saveCommand">
                    <v-card-title>{{ editingCode === null ? 'New command' : 'Edit command' }}</v-card-title>
                    <v-card-text>
                        <v-alert v-if="editError" type="error" class="mb-4">{{ editError }}</v-alert>
                        <v-text-field v-model="editItem.cmd_code" label="M-Code*" :readonly="saving" required />
                        <v-text-field v-model="editItem.cmd_name" label="Name*" :readonly="saving" required />
                        <v-text-field v-model="editItem.cmd_command" label="Command to execute on SBC*" :readonly="saving" required />
                        <v-text-field v-model.number="editItem.cmd_timeout" label="Timeout (seconds, 0 = unlimited)*"
                                      type="number" min="0" step="1" :readonly="saving" required />
                        <v-switch v-model="editItem.cmd_enabled" label="Enabled" :disabled="saving" />
                        <v-switch v-model="editItem.cmd_capture_output" label="Hide output" :disabled="saving" />
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer />
                        <v-btn variant="text" :disabled="saving" @click="editDialog = false">Close</v-btn>
                        <v-btn type="submit" color="primary" :loading="saving">Save</v-btn>
                    </v-card-actions>
                </v-form>
            </v-card>
        </v-dialog>
        <confirm-dialog v-model:shown="confirmDelete" title="Confirm delete" :prompt="`Delete command ${deleteCode}?`" @confirmed="deleteCommand" />
    </v-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useMachineStore } from "@/stores/machine";
import { nextAvailableCode, validateCommand, type Command } from "./commands";
import { configPath, readCommands, writeCommands } from "./configuration";

const machine = useMachineStore();
const commands = ref<Command[]>([]);
const loading = ref(false), saving = ref(false), editDialog = ref(false), confirmDelete = ref(false);
const error = ref(""), editError = ref("");
const editingCode = ref<string | null>(null), deleteCode = ref<string | null>(null);
const editItem = ref<Command>(blankCommand());
const headers = [
    { title: "M-Code", key: "cmd_code" }, { title: "Name", key: "cmd_name" },
    { title: "Command", key: "cmd_command" }, { title: "Enabled", key: "cmd_enabled" },
    { title: "Timeout", key: "cmd_timeout" }, { title: "Actions", key: "actions", sortable: false }
];

function blankCommand(): Command {
    return { cmd_code: "M1201", cmd_name: "", cmd_command: "", cmd_enabled: true, cmd_timeout: 30, cmd_capture_output: false };
}

function errorMessage(value: unknown): string {
    return value instanceof Error ? value.message : String(value);
}

const transport = {
    read: () => machine.download({ filename: configPath, type: "json" }, false, false, false),
    write: (content: Blob) => machine.upload({ filename: configPath, content }, false, false),
    reload: () => machine.sendCode("M1200")
};

async function reloadCommands() {
    loading.value = true;
    error.value = "";
    try {
        commands.value = await readCommands(transport);
    } catch (e) {
        error.value = `Could not load the command configuration. ${errorMessage(e)}`;
    } finally { loading.value = false; }
}

function newCommand() {
    editCommand({ ...blankCommand(), cmd_code: nextAvailableCode(commands.value) }, true);
}

function editCommand(command: Command, isNew = false) {
    editingCode.value = isNew ? null : command.cmd_code;
    // Editing a copy keeps Cancel from mutating the live command list.
    editItem.value = { ...command };
    editError.value = "";
    editDialog.value = true;
}

async function persist(next: Command[]) {
    saving.value = true;
    try {
        await writeCommands(transport, next);
        commands.value = next;
    } finally { saving.value = false; }
}

async function saveCommand() {
    const command = { ...editItem.value, cmd_code: editItem.value.cmd_code.trim().toUpperCase(), cmd_timeout: Number(editItem.value.cmd_timeout) };
    editError.value = validateCommand(command, commands.value, editingCode.value) ?? "";
    if (editError.value) return;
    const next = editingCode.value === null ? [...commands.value, command]
        : commands.value.map(item => item.cmd_code === editingCode.value ? command : item);
    try {
        await persist(next);
        editDialog.value = false;
    } catch (e) { editError.value = errorMessage(e); }
}

async function deleteCommand() {
    if (deleteCode.value === null) return;
    error.value = "";
    try { await persist(commands.value.filter(item => item.cmd_code !== deleteCode.value)); }
    catch (e) { error.value = errorMessage(e); }
    finally { deleteCode.value = null; }
}

onMounted(reloadCommands);
</script>
