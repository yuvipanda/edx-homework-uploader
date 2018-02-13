const path = require('path');

module.exports = {
  entry: './homeworkupload/static/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'homeworkupload/static/dist')
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [ 'style-loader', 'css-loader' ]
      }
    ]
  }
};
