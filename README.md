# Animate Me

Animate DOM Elements when they enter/leave the browser viewport

## Install

```
npm i animateme
```

or 

```
yarn add animateme
```

## Usage

In your HTML create the elements that you want to be animated.
The default classname used for the animations is `animate-me`.

Then

```
import AnimateMe from 'animateme';
```

and create a new instance with the default settings

```
new AnimateMe();
```

or use your own settings

```
new AnimateMe('.your-element', {
  offset: 0.8,
  reverse: false,
  animatedIn: 'your-custom-classname',
  offsetAttr: 'data-offset-top',
  animationAttr: 'data-animation-name',
  touchDisabled: false
})
```

If you wish to use the defaults, make sure to include the predefined css file. 

AnimateMe assumes you have modern JS environment and are using a module bundler such as Webpack.

If you wish to support older browsers, such as IE 11, you should include a polyfill for `Object.assign`.

## Options

1. Set your own classname for the animated element when in viewport:

	`animatedIn: 'animate-me--in'`

2. Set the animation delay in pixels via "data-offset" attribute. This attribute is added to the HTML element you want to animate. You can change this attrubute name in the options:

	`data-offset="120"`

3. Choose to disable the animations on touch devices 

	`mobileDisabled: false`

4. Choose the start point of the animation relatively to the viewport:

	`offset: 0.8`

	0.8 means that the animation will start when the top of the element is at 80% from the top of the viewport

	This number should be between 0 and 1.

5. Choose whether to run the animation every time the element enter the viewport:

	`reverse: false`

6. Optionally, you can use an external library such as [Animate.css](https://daneden.github.io/animate.css/). If you choose to do so, make sure that you add the animation name in the `data-animation` attribute of your DOM element. You can modify this attribute name in the options:

  `data-animation="bounce"`

## Supported Browsers

All browsers which know CSS transitions are supported.

IE9 and below will simply ignore the transitions and show the content as is.

Just remember to add all vendor prefixes, just in case :)

## Default setup:

```
new AnimateMe('.animated', {
  offset: 0.5,                     // Element will animate in when above the half of the viewport
  reverse: true,                   // Element will animate out when below the half of the viewport
  animatedIn: 'animate-me--in',    // Classname to add to the element when above half of the viewport
  offsetAttr: 'data-offset',       // Element's offset attribute
  animationAttr: 'data-animation', // Element's custom animation name
  touchDisabled: true              // Animations will not run on touch devices
});
```

## Demo

Please see [this pen](https://codepen.io/scriptex/pen/YYKRXK)
