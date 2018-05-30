[![GitHub stars](https://img.shields.io/github/stars/scriptex/AnimateMe.svg?style=social&label=Stars)](https://github.com/scriptex/AnimateMe)
[![GitHub forks](https://img.shields.io/github/forks/scriptex/AnimateMe.svg?style=social&label=Fork)](https://github.com/scriptex/AnimateMe/network#fork-destination-box)
[![GitHub release](https://img.shields.io/github/release/scriptex/AnimateMe.svg)](https://github.com/scriptex/AnimateMe/releases/latest)
[![GitHub issues](https://img.shields.io/github/issues/scriptex/AnimateMe.svg)](https://github.com/scriptex/AnimateMe/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/scriptex/AnimateMe.svg)](https://github.com/scriptex/AnimateMe/commits/master)
[![Github file size](https://img.shields.io/github/size/scriptex/AnimateMe/dist/animate.me.min.js.svg)](https://github.com/scriptex/AnimateMe)
[![Build Status](https://travis-ci.org/scriptex/AnimateMe.svg?branch=master)](https://travis-ci.org/scriptex/AnimateMe)
[![npm](https://img.shields.io/npm/dt/animateme.svg)](https://www.npmjs.com/package/animateme)
[![npm](https://img.shields.io/npm/v/animateme.svg)](https://www.npmjs.com/package/animateme)
[![license](https://img.shields.io/github/license/scriptex/AnimateMe.svg)](https://github.com/scriptex/AnimateMe)
[![Analytics](https://ga-beacon.appspot.com/UA-83446952-1/github.com/scriptex/AnimateMe/README.md)](https://github.com/scriptex/AnimateMe/)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/scriptex/AnimateMe/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/scriptex/AnimateMe/graphs/commit-activity)

[![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)](https://github.com/scriptex/)

# Animate Me

Animate DOM elements when they enter/leave the browser viewport.

This library uses a small amount on JavaScript and leaves the actual animations to the CSS.

You have the freedom to implement your own animations, use predefined (via another library) or use the built-in fade in/out animation.

## Dependencies

There are no dependencies and the library is ready to be used in any environment.

If you, however, wish to develop the library, extend it, fix it, etc, you need to install its development dependencies.

## Install

```console
npm i animateme
```

or

```console
yarn add animateme
```

or

just download this repository and use the files located in `dist` folder.

## Usage

In your HTML create the elements that you want to be animated.

The default class name used for the animations is `animate-me`.

Then

```javascript
import AnimateMe from 'animateme';
```

and create a new instance with the default settings

```javascript
new AnimateMe();
```

or use your own settings

```javascript
new AnimateMe('.your-element', {
  offset: 0.8,
  reverse: false,
  animatedIn: 'your-custom-class',
  offsetAttr: 'data-offset-top',
  animationAttr: 'data-animation-name',
  touchDisabled: false
});
```

If you wish to use the defaults, make sure to include the predefined CSS file.

```css
@import 'animateme/dist/animate.me.css';
```

or just use it as a good old `<link>` tag.

## Options

1.  Set your own classname for the animated element when in viewport:

    `animatedIn: 'animate-me--in'`

2.  Set the animation delay in pixels via `"data-offset"` attribute. This attribute is added to the HTML element you want to animate. You can change this attrubute name in the options:

    `data-offset="120"`

3.  Choose to disable the animations on touch devices

    `touchDisabled: false`

4.  Choose the start point of the animations relatively to the viewport:

    `offset: 0.8`

    0.8 means that all animations will start when the top of the element is at 80% from the top of the viewport

    This number should be between 0 and 1.

5.  Choose whether to run the animation every time the element enter the viewport:

    `reverse: false`

6.  Optionally, you can use an external library such as [Animate.css](https://daneden.github.io/animate.css/). If you choose to do so, make sure that you add the animation name in the `data-animation` attribute of your DOM element. You can modify this attribute name in the options:

`data-animation="bounce"`

## Supported Browsers

All browsers which know CSS transitions are supported.

IE9 and below will simply ignore the transitions and show the content as is.

Just remember to add all CSS vendor prefixes, just in case :)

## Default setup:

```javascript
new AnimateMe('.animate-me', {
  offset: 0.5, // Element will animate in when above the half of the viewport
  reverse: true, // Element will animate out when below the half of the viewport
  animatedIn: 'animate-me--in', // Class name to add to the element when above half of the viewport
  offsetAttr: 'data-offset', // Element's offset attribute
  animationAttr: 'data-animation', // Element's custom animation name
  touchDisabled: true // Animations will not run on touch devices
});
```

## Destroy animations / event listeners

If you want to stop AnimateMe, there are two ways to do so:

1.  Calling `unbind` on the instance will remove all event listeners which will cause your animations to stop working.
2.  Calling `cleanup` on the instance will remove all CSS classes set to your elements by AnimateMe.
3.  Calling `destroy` on the instance will remove all event listeners and all CSS classes set to your elements by AnimateMe, effectively restoring their initial state.

Example:

```javascript
const instance = new AnimateMe();

// Remove event listeners but keep the CSS classes
instance.unbind();

// Remove CSS classes from all elements
instance.cleanup();

// Remove event listeners and the CSS classes
instance.destroy();
```

## Trigger custom events

It is possible to control the AnimateMe instance via custom events.
The custom events are called on the `window` object.

There are three events implemented:

1.  `animateme:enable`: Enables the instance. Equals to a call to `start` on the instance.
2.  `animateme:destroy`: Destroys the instance. Equals to a call to `destroy` on the instance.
3.  `animateme:cleanup`: Cleans previously set CSS classes to AnimateMe elements. Equals to a call to `cleanup` on the instance.

Example usage of custom events:

```javascript
// First create the custom events
const enable = new CustomEvent('animateme:enable');
const destroy = new CustomEvent('animateme:destroy');
const cleanup = new CustomEvent('animateme:cleanup');

// Then dispatch an event
window.dispatchEvent(cleanup);
window.dispatchEvent(destroy);
window.dispatchEvent(enable);
```

**Important note:**

**Internet Explorer [does not fully support](https://caniuse.com/#feat=customevent) `new CustomEvent`.**

**You have to create the custom events in a way that IE understands it.**

**Something like: `document.createEvent('CustomEvent')`.**

## Demo

There is a simple demo illustrating how the AnimateMe library works.

Check it out [here](https://github.com/scriptex/AnimateMe/blob/master/demo/index.html) or [here](https://codepen.io/scriptex/full/YYKRXK/).

## LICENSE

MIT
