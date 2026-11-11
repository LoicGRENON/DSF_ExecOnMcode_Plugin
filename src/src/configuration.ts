import type { Command } from "./commands";

export const configPath = "0:/sys/ExecOnMcode/ExecOnMcode.json";

export interface ConfigurationTransport {
    read(): Promise<unknown>;
    write(content: Blob): Promise<unknown>;
    reload(): Promise<unknown>;
}

export async function readCommands(transport: ConfigurationTransport): Promise<Command[]> {
    const response = await transport.read();
    if (!Array.isArray(response)) throw new Error("The plugin configuration is not a command list.");
    return response.map(item => {
        if (item === null || typeof item !== "object" || typeof item.cmd_code !== "string" || typeof item.cmd_command !== "string") {
            throw new Error("The plugin configuration contains an invalid command.");
        }
        // Match MCodeAction defaults for fields omitted by hand-written configurations.
        return {
            cmd_name: "", cmd_enabled: true, cmd_timeout: 30, cmd_capture_output: false,
            ...item
        };
    });
}

export async function writeCommands(transport: ConfigurationTransport, commands: Command[]): Promise<void> {
    await transport.write(new Blob([JSON.stringify(commands, null, 4)], { type: "application/json" }));
    // Reload filters only after a successful upload; never execute a configured command.
    await transport.reload();
}
