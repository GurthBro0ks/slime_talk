// Run only on the selected private controller host. No keys are printed.
import {randomBytes} from 'node:crypto';import {writeFileSync} from 'node:fs';
const file=process.argv[2];if(!file)throw Error('Supply a private output path outside Git');
writeFileSync(file,JSON.stringify({pixel:randomBytes(32).toString('base64url'),iphone:randomBytes(32).toString('base64url')})+'\n',{mode:0o600,flag:'wx'});
console.log('Device authorization file created. Transfer each key privately only to its corresponding phone.');
