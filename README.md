# Tidsram

Swedish word clock for Raspberry Pi with WS2812B LEDs.

## Inspiration

The code and build is inspired by the following makers:

- [rpi_wordclock](https://github.com/bk1285/rpi_wordclock) by [bk1285](https://github.com/bk1285)
- [LED Word Clock](https://www.youtube.com/watch?v=SXYwSN6mX_Q) by [Chloe Kuo](https://www.youtube.com/channel/UC0ybj4KuDQc_jOx1ONrlrfw)

## Features

- Display the current time with resolution of five minutes.
- Pygame to run the main loop consistently.
- Abstract display allows development without access to WS2812B LEDs.

## Font

D-DIN font by Datto licensed under the [SIL Open Font License (OFL)](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL).

## Configuration

A configuration file allows the user to make adjustments to the application. Such as: LED brightness & color, run simulated time etc.
Make a copy of `settings.conf.example`, save it as `settings.conf` and then change the available fields to suitable values.
The configuration is read when the application starts, so make sure to restart the application for the change to take effect.
