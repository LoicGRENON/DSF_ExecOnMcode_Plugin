import test from 'node:test';
import assert from 'node:assert/strict';
import { nextAvailableCode, validateCommand } from '../src/src/commands.ts';

const command = code => ({ cmd_code: code, cmd_name: 'Example', cmd_command: 'echo example', cmd_timeout: 30, cmd_enabled: true, cmd_capture_output: false });

test('allocates the first free M-code even when the list is unsorted', () => {
    assert.equal(nextAvailableCode([command('M1203'), command('M1201')]), 'M1202');
});
test('rejects duplicate codes when adding and renaming', () => {
    const commands = [command('M1201'), command('M1202')];
    assert.ok(validateCommand(command('M1201'), commands, null));
    assert.ok(validateCommand(command('M1201'), commands, 'M1202'));
    assert.equal(validateCommand(command('M1201'), commands, 'M1201'), null);
});
test('protects the reload code and rejects non-M codes', () => {
    for (const code of ['M1200', 'M1200.1', 'M01200', 'G28', 'M12\nM999', '']) assert.ok(validateCommand(command(code), [], null));
});
test('allows zero timeout and rejects invalid or negative timeouts', () => {
    assert.equal(validateCommand({ ...command('M1201'), cmd_timeout: 0 }, [], null), null);
    for (const timeout of [-1, NaN, Infinity, 1.5]) assert.ok(validateCommand({ ...command('M1201'), cmd_timeout: timeout }, [], null));
});
