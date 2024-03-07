const path = require('path');
const webpack = require('webpack');

module.exports = {
    mode: 'development',
    devtool: 'eval-source-map',
    entry: './ui/index.tsx',
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                exclude: /node_modules/,
                use: [
                    // {
                    //     loader: 'babel-loader',
                    //     options: {
                    //         presets: ['@babel/preset-env', '@babel/preset-typescript', '@babel/preset-react'],
                    //         plugins: [
                    //             "@babel/plugin-transform-runtime"
                    //         ]
                    //     }
                    // },
                    'ts-loader'
                ]
            }
        ]
    },
    resolve: {
        extensions: ['*', '.js', '.jsx', '.ts', '.tsx']
    },
    output: {
        path: path.resolve(__dirname, 'static/js'),
        filename: 'bundle.js',
        publicPath: '/js/' // This ensures assets are served relative to root
    },
    devServer: {
        static: path.join(__dirname, 'static'), // replaced 'contentBase' with 'static'
        port: 9000,
        hot: true,
        proxy: {
            '/api/': {
                target: 'http://127.0.0.1:5000/',
                changeOrigin: true, // this option is important
                secure: false,
                logLevel: 'debug'  // this will log proxy requests to the console
            }
        },
    },
    plugins: [
        // new webpack.HotModuleReplacementPlugin(),
    ]
};
