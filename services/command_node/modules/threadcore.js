// modules/threadcore.js
module.exports = {
  init: opts => console.log('THREADCORE.init', opts),
  seed: payload => console.log('THREADCORE.seed', payload),
  update: payload => console.log('THREADCORE.update', payload),
  reflect: () => console.log('THREADCORE.reflect'),
};
