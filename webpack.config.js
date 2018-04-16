const UnminifiedWebpackPlugin = require('unminified-webpack-plugin');

module.exports = {
	mode: 'production',
	entry: './src/animate.me.js',
	output: {
		filename: 'animate.me.min.js',
		library: 'AnimateMe',
		libraryTarget: 'umd',
		libraryExport: 'default'
	},
	module: {
		rules: [
			{
				test: /\.(js)$/,
				loader: 'babel-loader'
			}
		]
	},
	plugins: [new UnminifiedWebpackPlugin()]
};
