module.exports = {
    // Extend any existing configurations you might have
    extends: [
      'react-app',  // This is likely already in use since you're using React
      'react-app/jest'
    ],
    // Add rules to override default behavior
    rules: {
      // You can customize specific rules here
    },
    // This section will help ignore the html5-qrcode source map warnings
    overrides: [
      {
        files: ['**/node_modules/html5-qrcode/**/*.js'],
        rules: {
          // This disables source map warnings for the html5-qrcode package
          'source-map-loader/no-missing-source-map': 'off'
        }
      }
    ]
  };