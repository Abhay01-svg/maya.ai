const io = require('socket.io-client');

const QUESTIONS = [
  'What is 13 multiplied by 7?',
  'What is the capital of Japan?',
  'Who was the first person to walk on the Moon?',
  'What causes rainbows to form in the sky?',
  'How do you reverse a string in Python?'
];

const socketOptions = {
  reconnectionAttempts: 8,
  timeout: 20000,
  reconnectionDelay: 500,
  reconnectionDelayMax: 2000
};
const socket = io('http://localhost:3000', socketOptions);

socket.on('connect', () => {
  console.log('Connected to Node VUI:', socket.id);
  runQuestions().then(() => {
    console.log('All done.');
    socket.disconnect();
    process.exit(0);
  }).catch(err => {
    console.error('Error during run:', err);
    socket.disconnect();
    process.exit(2);
  });
});

socket.on('connect_error', (err) => {
  console.error('Connection error:', err.message || err);
});

socket.on('disconnect', () => {
  console.log('Disconnected from Node VUI');
});

function emitQuestion(text, timeout = 20000) {
  return new Promise((resolve, reject) => {
    let settled = false;
    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        reject(new Error('timeout waiting for maya-reply'));
      }
    }, timeout);

    socket.once('maya-reply', (reply) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve(reply);
    });

    socket.emit('voice-data', text);
  });
}

async function runQuestions() {
  for (const q of QUESTIONS) {
    console.log('\n-> Question:', q);
    try {
      const reply = await emitQuestion(q);
      console.log('   Maya reply:', reply);
    } catch (err) {
      console.error('   Error:', err.message || err);
    }
  }
}
