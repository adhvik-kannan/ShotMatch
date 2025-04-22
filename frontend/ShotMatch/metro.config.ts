// metro.config.js
const { getDefaultConfig } = require('@expo/metro-config');
const os = require('os');

const config = getDefaultConfig(__dirname);

// override maxWorkers to use os.cpus().length instead of availableParallelism()
config.maxWorkers = os.cpus().length;

module.exports = config;
