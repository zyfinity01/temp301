# Device Software

This directory holds the following subdirectories and files:

```text
device
├── build/
├── embedded/
├── webapp/
└── build.sh
```

- `build`: automatically created by the software build script, `build.sh` (see below).
- `embedded`: Micropython device code &mdash; development takes place here.
- `webapp`: preact web app code &mdash; development takes place here.
- `build.sh`: a build script that combines the output of the build scripts in the subdirectories, `build-webapp.sh` and `build-device.sh`, into a ready-to-upload `build/` directory with compiled micropython and preact code.
