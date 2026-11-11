export interface Command {
    cmd_code: string;
    cmd_name: string;
    cmd_command: string;
    cmd_enabled: boolean;
    cmd_timeout: number;
    cmd_capture_output: boolean;
    [key: string]: unknown;
}

export function nextAvailableCode(commands: Command[]): string {
    const used = new Set(commands.map(command => command.cmd_code.toUpperCase()));
    let number = 1201;
    while (used.has(`M${number}`)) number++;
    return `M${number}`;
}

export function validateCommand(command: Command, commands: Command[], editingCode: string | null): string | null {
    if (!/^M\d+(?:\.\d+)?$/.test(command.cmd_code) || /^M0*1200(?:\.|$)/.test(command.cmd_code)) {
        return "Enter an M-Code; M1200 is reserved for reloading the plugin.";
    }
    if (commands.some(item => item.cmd_code.toUpperCase() === command.cmd_code && item.cmd_code !== editingCode)) {
        return "This M-Code is already configured.";
    }
    if (!command.cmd_name.trim() || !command.cmd_command.trim()) return "Name and command are required.";
    if (!Number.isInteger(command.cmd_timeout) || command.cmd_timeout < 0) {
        return "Timeout must be a whole number of seconds (0 means no timeout).";
    }
    return null;
}
