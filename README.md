[![Travis CI](https://travis-ci.com/scriptex/AnimateMe.svg?branch=master)](https://travis-ci.com/scriptex/AnimateMe)
[![Github Build](https://github.com/scriptex/AnimateMe/workflows/Build/badge.svg)](https://github.com/scriptex/AnimateMe/actions?query=workflow%3ABuild)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/34d3d75710534dc6a38c3584a1dcd068)](https://www.codacy.com/gh/scriptex/AnimateMe/dashboard?utm_source=github.com&utm_medium=referral&utm_content=scriptex/AnimateMe&utm_campaign=Badge_Grade)
[![Codebeat Badge](https://codebeat.co/badges/d765a4c8-2c0e-44f2-89c3-fa364fdc14e6)](https://codebeat.co/projects/github-com-scriptex-animateme-master)
[![CodeFactor Badge](https://www.codefactor.io/repository/github/scriptex/animateme/badge)](https://www.codefactor.io/repository/github/scriptex/animateme)
[![DeepScan grade](https://deepscan.io/api/teams/3574/projects/5257/branches/40799/badge/grade.svg)](https://deepscan.io/dashboard#view=project&tid=3574&pid=5257&bid=40799)
[![Analytics](https://ga-beacon-361907.ew.r.appspot.com/UA-83446952-1/github.com/scriptex/AnimateMe/README.md?pixel)](https://github.com/scriptex/AnimateMe/)

# Animate Me

Animate DOM elements when they enter/leave the browser viewport.

This library uses a small amount on JavaScript and leaves the actual animations to the CSS.

You have the freedom to implement your own animations, use predefined (via another library) or use the built-in fade in/out animation.

## Visitor stats

![GitHub stars](https://img.shields.io/github/stars/scriptex/AnimateMe?style=social)
![GitHub forks](https://img.shields.io/github/forks/scriptex/AnimateMe?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/scriptex/AnimateMe?style=social)
![GitHub followers](https://img.shields.io/github/followers/scriptex?style=social)

## Code stats

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/scriptex/AnimateMe)
![GitHub repo size](https://img.shields.io/github/repo-size/scriptex/AnimateMe?style=plastic)
![GitHub language count](https://img.shields.io/github/languages/count/scriptex/AnimateMe?style=plastic)
![GitHub top language](https://img.shields.io/github/languages/top/scriptex/AnimateMe?style=plastic)
![GitHub last commit](https://img.shields.io/github/last-commit/scriptex/AnimateMe?style=plastic)

## Dependencies

There are no dependencies and the library is ready to be used in any environment.

If you, however, wish to develop the library, extend it, fix it, etc, you need to fork this repository and install its development dependencies.

## Install

```sh
npm i animateme

# or

yarn add animateme
```

## Usage

In your HTML create the elements that you want to be animated.

The default class name used for the animations is `animate-me`.

Then

```javascript
import AnimateMe from 'animateme';

// or

import { AnimateMe } from 'animateme';
```

and create a new instance with the default settings

```javascript
new AnimateMe();
```

or use your own options

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

**Note**

Using `AnimateMe` via a good old `<script>` tag is currently supported only using helper libraries such as `requirejs`, `systemjs`, etc.

```html
<!-- Import the Require JS script -->
<script src="https://unpkg.com/requirejs"></script>

<!-- Then require the AnimateMe script from your local folder and use it -->
<script>
	require(['./your/scripts/folder/animate.me.js'], function ({ AnimateMe }) {
		new AnimateMe();

		// or with custom options

		new AnimateMe('.your-element', {
			offset: 0.8,
			reverse: false,
			animatedIn: 'your-custom-class',
			offsetAttr: 'data-offset-top',
			animationAttr: 'data-animation-name',
			touchDisabled: false
		});
	});
</script>
```

For the best experience please use a module bundler such as Webpack, Parcel, Rollup or Browserify.

---

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

## API

AnimateMe provides you with access to its API - class methods which allow you to have full control over the instance and its properties.

**You should use this API with caution.**

First, you need to have an initialized instance of the `AnimateMe` class:

```javascript
const instance = new AnimateMe();
```

### Then you can modify the instance properties:

```javascript
/**
 * Update the options of the AnimateMe instance
 */
instance.options = {
	offset: 0.5,
	reverse: true,
	animatedIn: 'animate-me--in',
	offsetAttr: 'data-offset',
	animationAttr: 'data-animation',
	touchDisabled: true
};

/**
 * Update the elements which the instance is animating.
 * Useful after programmatiacally updating the DOM (for example after AJAX call)
 */
instance.animated = Array.from(document.querySelectorAll('.your-new-selector'));
instance.updateInstance();

/**
 * Update the CSS selector for the animating elements.
 * You should not need to change this.
 */
instance.selector = '.your-new-selector';
instance.updateInstance();
```

### You can use the following public instance methods:

```typescript
/**
 * Gets the value of the window.pageYOffset property
 * and assigns it to a private class property used to
 * calculate offsets and animate DOM elements.
 */
setCurrentScroll();

/**
 * Gets the value of the window.innerHeight property
 * and assigns it to a private class property used to
 * calculate offsets and animate DOM elements.
 */
getWindowDimensions();

/**
 * Attaches event listeners to the document.
 * Useful after the listeners have been removed for some reason.
 */
bind();

/**
 * Removes the event listeners from the document.
 * Useful if you want to cleanup after removing all animated
 * DOM elements.
 */
unbind();

/**
 * Removes the `animatedIn` classname from all animated elements.
 */
cleanup();

/**
 * Removes the event listeners from the document.
 * Removes the `animatedIn` classname from all animated elements.
 * Shortcut to calling both unbind() and cleanup()
 */
destroy();

/**
 * Triggers the animation for all elements.
 */
animate();

/**
 * Sets the elements which need to be animated.
 * Useful after DOM updates (like AJAX calls or similar).
 */
setElements();

/**
 * Updates the `offsets` class property which is used
 * to animate the elements.
 */
updateOffsets();

/**
 * Updates the whole instance.
 * @param {Boolean} shouldAnimate Flag based on which the `animate()` method is called.
 */
updateInstance(shouldAnimate: boolean = false);
```

## Bonus

If you chose to use the predefined classnames `animate-me` and `animate-me--in` then you can take advantage of the built-in animations.
Just include the css file (`/dist/animate.me.css`) in your project and then add additional classname to your animated elements.

There are several predefined animations and their classnames are:

-   `animate-me--fadeIn`
-   `animate-me--slideUp`
-   `animate-me--slideDown`
-   `animate-me--slideLeft`
-   `animate-me--slideRight`
-   `animate-me--pop`

## TypeScript support

TypeScript is supported out of the box. The types declaration file should be automatically picked up by TypeScript.

The TypeScript declaration file is located in the `/dist` folder.

If you want to use the raw TypeScript version of the module:

```typescript
import AnimateMe from 'animate-me/src/animate-me';

// and then use it as shown above
```

## Demo

There is a simple demo illustrating how the AnimateMe library works.

Check it out [here](https://animate-me.atanas.info/).

## LICENSE

MIT

---

<div align="center">
    Connect with me:
</div>

<br />

<div align="center">
    <a href="https://atanas.info">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/logo.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="mailto:hi@atanas.info">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/email.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://www.linkedin.com/in/scriptex/">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/linkedin.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://github.com/scriptex">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/github.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://gitlab.com/scriptex">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/gitlab.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://twitter.com/scriptexbg">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/twitter.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://www.npmjs.com/~scriptex">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/npm.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://www.youtube.com/user/scriptex">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/youtube.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://stackoverflow.com/users/4140082/atanas-atanasov">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/stackoverflow.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://codepen.io/scriptex/">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/codepen.svg" width="20" alt="">
    </a>
    &nbsp;
    <a href="https://profile.codersrank.io/user/scriptex">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/codersrank.svg" height="20" alt="">
    </a>
    &nbsp;
    <a href="https://linktr.ee/scriptex">
        <img src="https://raw.githubusercontent.com/scriptex/socials/master/styled-assets/linktree.svg" height="20" alt="">
    </a>
</div>

---

<div align="center">
Support and sponsor my work:
<br />
<br />
<a href="https://twitter.com/intent/tweet?text=Checkout%20this%20awesome%20developer%20profile%3A&url=https%3A%2F%2Fgithub.com%2Fscriptex&via=scriptexbg&hashtags=software%2Cgithub%2Ccode%2Cawesome" title="Tweet">
	<img src="https://img.shields.io/badge/Tweet-Share_my_profile-blue.svg?logo=twitter&color=38A1F3" />
</a>
<a href="https://paypal.me/scriptex" title="Donate on Paypal">
	<img src="https://img.shields.io/badge/Donate-Support_me_on_PayPal-blue.svg?logo=paypal&color=222d65" />
</a>
<a href="https://revolut.me/scriptex" title="Donate on Revolut">
	<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/scriptex/scriptex/master/badges/revolut.json" />
</a>
<a href="https://patreon.com/atanas" title="Become a Patron">
	<img src="https://img.shields.io/badge/Become_Patron-Support_me_on_Patreon-blue.svg?logo=patreon&color=e64413" />
</a>
<a href="https://ko-fi.com/scriptex" title="Buy Me A Coffee">
	<img src="https://img.shields.io/badge/Donate-Buy%20me%20a%20coffee-yellow.svg?logo=ko-fi" />
</a>
<a href="https://liberapay.com/scriptex/donate" title="Donate on Liberapay">
	<img src="https://img.shields.io/liberapay/receives/scriptex?label=Donate%20on%20Liberapay&logo=liberapay" />
</a>

<a href="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/scriptex/scriptex/master/badges/bitcoin.json" title="Donate Bitcoin">
	<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/scriptex/scriptex/master/badges/bitcoin.json" />
</a>
<a href="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/scriptex/scriptex/master/badges/etherium.json" title="Donate Etherium">
	<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/scriptex/scriptex/master/badges/etherium.json" />
</a>
<a href="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/scriptex/scriptex/master/badges/shiba-inu.json" title="Donate Shiba Inu">
	<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/scriptex/scriptex/master/badges/shiba-inu.json" />
</a>
</div>
