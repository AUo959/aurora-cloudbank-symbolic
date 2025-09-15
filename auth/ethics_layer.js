exports.ethicsCheck = function(command) {
  const forbidden = ['blacklist', 'override'];
  if (
    !command ||
    typeof command !== 'object' ||
    typeof command.name !== 'string' ||
    command.name.trim() === ''
  ) {
    return false;
  }
  return !forbidden.includes(command.name.toLowerCase());
};

exports.anchorResolve = function(context) {
  return `ANCHOR_${context}_HASH`;
};
