exports.ethicsCheck = function (command) {
  const forbidden = ['blacklist', 'override'];
  return !forbidden.includes(command.name.toLowerCase());
};

exports.anchorResolve = function (context) {
  return `ANCHOR_${context}_HASH`;
};
