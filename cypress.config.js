const { defineConfig } = require("cypress");

module.exports = defineConfig({
  fixturesFolder: 'cypress/fixtures',
  e2e: {
    watchForFileChanges: false,
    setupNodeEvents(on, config) {
      const environmentName = config.env.environmentName || 'docker'
      const environmentFilename = `./${environmentName}.settings.json`
      console.log('loading %s', environmentFilename)
      const settings = require(environmentFilename)
      if (settings.baseUrl) {
        config.baseUrl = settings.baseUrl
      }
      if (settings.env) {
        config.env = {
          ...config.env,
          ...settings.env,
        }
      }
      console.log('loaded settings for environment %s', environmentName)
    
      // IMPORTANT: return the updated config object
      // for Cypress to use it
      return config
    },
  },
});
