// node analysis/check_diff_line.ts
import assert from 'node:assert/strict';
import { diffLine } from '../src/lib/content/diff.ts';

const hot = (text: string) => `<span class="diff">${text}</span>`;

assert.equal(diffLine('Some((0, 1))', ['(0, 1)']), `${hot('Some')}${hot('(')}(0, 1)${hot(')')}`);
assert.equal(diffLine('(0, 1)', ['Some((0, 1))']), '(0, 1)');
assert.equal(diffLine('Some(4)', ['4']), `${hot('Some')}${hot('(')}4${hot(')')}`);
assert.equal(diffLine('Some("a b")', ['"a b"']), `${hot('Some')}${hot('(')}"a b"${hot(')')}`);
assert.equal(diffLine('[1, 2]', ['[1, 2]']), '[1, 2]');
console.log('ok');
