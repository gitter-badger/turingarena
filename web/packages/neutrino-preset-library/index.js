const nodeExternals = require("webpack-node-externals");

module.exports = (neutrino, opts = {}) => neutrino
  .use(require.resolve('@neutrinojs/library'), opts)
  .use(require.resolve('@turingarena/neutrino-middleware-babel'))
  .config.externals([nodeExternals({
    modulesFromFile: true,
  })])
  // see https://github.com/mozilla-neutrino/neutrino-dev/issues/987  
