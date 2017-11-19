# Animate Me

Animate DOM Elements when they enter the browser viewport

## Usage

In your HTML create the elements that you want to be animated.
The default classname used for the animations is `animate-me`.

Then
```
import AnimateMe from 'animateme';
```

and initialize the constructor with
```
new AnimateMe();
```

If you wish to use the defaults, make sure to add the predefined css file or add your own.

## Options

1. Set your own classname for the animated element when in viewport. 

	`animatedIn: 'animated-in'`

2. Set the animation delay in pixels via "data-offset" attribute. You can change this attrubute name in the options.

	`data-offset="120"`

3. Choose to disable the animations on touch devices 

	`mobileDisabled: false`

4. Choose the start point of the animation relatively to the viewport.

	`offset: 0.8`

	0.8 means that the animation will start when the top of the element is at 80% from the top of the viewport

	This number should be between 0 and 1.

5. Choose whether to run the animation again as you scroll up and then down

	`reverse: false`

6. Optionally, you can use an external library such as `animates.css`. If you choose to do so make sure that you add the animation name in the `data-animation` attribute of your DOM element. You can modify this attribute name in the options.

## Supported Browsers

All browsers which know CSS transitions are supported.

IE9 and below will simply ignore the transitions and show the content as is.

Just remember to add all vendor prefixes, just in case :)

## Example setup:

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
