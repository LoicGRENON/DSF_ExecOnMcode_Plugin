import test from 'node:test';
import assert from 'node:assert/strict';
import { readCommands, writeCommands } from '../src/src/configuration.ts';

test('reading configuration performs no writes or reloads', async () => {
    const result = await readCommands({
        read: async () => [{ cmd_code: 'M1201', cmd_command: 'example', custom_field: 'keep' }],
        write: async () => { assert.fail('read must not upload'); },
        reload: async () => { assert.fail('read must not send codes'); }
    });
    assert.equal(result[0].cmd_timeout, 30);
    assert.equal(result[0].custom_field, 'keep');
});

test('saving preserves fields and reloads only after uploading', async () => {
    const order = [];
    const commands = [{ cmd_code: 'M1201', cmd_command: 'example', cmd_timeout: 0, custom_field: 'keep' }];
    await writeCommands({
        read: async () => { assert.fail('save does not read'); },
        write: async blob => { order.push('write'); assert.deepEqual(JSON.parse(await blob.text()), commands); },
        reload: async () => { order.push('reload'); }
    }, commands);
    assert.deepEqual(order, ['write', 'reload']);
});

test('upload failure never reloads filters', async () => {
    await assert.rejects(writeCommands({
        read: async () => [],
        write: async () => { throw new Error('upload failed'); },
        reload: async () => { assert.fail('failed upload must not reload'); }
    }, []), /upload failed/);
});

test('reload failure is reported to the editor', async () => {
    await assert.rejects(writeCommands({
        read: async () => [], write: async () => {},
        reload: async () => { throw new Error('backend unavailable'); }
    }, []), /backend unavailable/);
});

test('invalid files are rejected before opening an editable list', async () => {
    for (const invalid of [{}, [null], [{ cmd_code: 'M1201' }]]) {
        await assert.rejects(readCommands({ read: async () => invalid }), /configuration/);
    }
});
