# Webapp Code

This directory stores the [Preact](https://preactjs.com/) code for running the webapp frontend on the embedded device.

## Setup

Simply run `npm install` from this folder to install the correct javascript depencies.

## Local Development

These steps are useful for developing the web-app without requiring access to the data logger.

You will need two terminals open - the mock server (simulates the tinyweb server in CPython) and the react dev server.

Terminal 1 (backend mock server):

1. ensure python virtualenv is activated
1. run `python ../../simulator/src/webserver.py`

Terminal 2 (react dev server):

1. run `npm install`
1. copy environment vars: `cp .env.example .env`
1. run `npm run dev`

## CLI Commands

- `npm install`: Installs dependencies

- `npm run dev`: Run a development, HMR server

- `npm run serve`: Run a production-like server

- `npm run build`: Production-ready build

- `npm run lint`: Pass TypeScript files using TSLint

- `npm run test`: Run Jest and Enzyme with
  [`enzyme-adapter-preact-pure`](https://github.com/preactjs/enzyme-adapter-preact-pure) for
  your tests

For detailed explanation on how things work, checkout the [CLI Readme](https://github.com/developit/preact-cli/blob/master/README.md).

## Shrinking the `build/` folder

**NOTE**: This folder is automatically pruned in the [build script](./build-webapp.sh).

Although the `build/` folder generates a lot of files, most are useless.

required files: `bundle.[hash].js`, `index.html`, and `bundle.[hash].css`.

you might need this:

- `*.bundle.esm.js` - enabling ESM imports as part of JS ECMA. Raises console errors if not included

What are the other files?

- `sw*` - Service Worker files. Service workers are for offline apps, push notifications etc (basically PWAs). Don't worry about them for now
- `polyfills.*` - polyfils are a compatibility layer to make code work on older devices (we aren't supporting older devices)
- `*.map` - source map files - good for debugging minified JS

## Other Notes

`dotenv-safe` was replaced with `dotenv` to have regain optional environment vars. Without `API_URL` set it will default to the local machine (relative url), otherwise it will use the environment var for the api. This means we can have a testing environment with a mock webserver for when developing.

---
