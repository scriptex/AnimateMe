# CSS and jQuery <br /> animations on scroll.

## Usage

1. Include <a href="https://daneden.github.io/animate.css/" target="_blank">animate.css</a> in your project.

2. Include animated.css in your project
	
3. Include <a href="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js" target="_blank">jQuery</a> in your project.
	
4. Include animated.min.js in your project.
	
5. Add "animated" classname to the element that you want to animate

6. Add the <a href="https://github.com/daneden/animate.css#readme" target="_blank">animation name</a> that you like as a "data-animation" attribute to the element: 

	`<li class="col-sm-3 animated" data-animation="rubberBand"></li>`

## Options

1. Set your own classname for the animated element when in viewport. Remember to update animated.css too!

	`animatedIn: 'animated-in'`

2. Set the animation delay in pixels via "data-offset" attribute

	`data-offset="120"`

3. Choose to run the animations on mobile devices (tablets and phones)

	`mobileDisabled: true`

4. Choose the start point of the animation relatively to the viewport.

	`offset: 0.8`

	0.8 means that the animation will start when the top of the element is at 80% from the top of the viewport

	This number should be between 0 and 1.

5. Choose whether to run the animation again as you scroll up and then down

	`reverse: false`

## Supported Browsers

All browsers which know CSS transitions are supported.

IE9 and below will simply ignore the transitions and show the content as is.

Just remember to add all vendor prefixes, just in case :)

## Example setup:

```
	$(document).ready(function() {
		$('.animated').animated({
			animatedIn: 'animated-in',
			offset: 0.8,
			reverse: false,
			mobileDisabled: true
		});
	});
```
