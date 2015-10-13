<h1>CSS and jQuery <br />animations on scroll.</h1>

<h2>Usage</h2>

<ol>
	<li>Include <a href="https://daneden.github.io/animate.css/" target="_blank">animate.css</a> in your project.</li>

	<li>Include animated.css in your project.</li>
	
	<li>Include <a href="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js" target="_blank">jQuery</a> in your project.</li>
	
	<li>Include animated.min.js in your project.</li>
	
	<li>Add "animated" classname to the element that you want to animate</li>

	<li>Add the <a href="https://github.com/daneden/animate.css#readme" target="_blank">animation name</a> that you like as a "data-animation" attribute to the element: 

		<br />

		<br />

		<code>
			&lt;li class="col-sm-3 animated" data-animation="rubberBand"&gt;&lt;/li&gt;
		</code>
	</li>
</ol>

<h2>Options</h2>

<ol>
	<li>
		<p>Set your own classname for the animated element when in viewport. Remember to update animated.css too!</p>

		<code>
			animatedIn: 'animated-in'
		</code>
	</li>

	<li>
		<p>Set the animation delay in pixels via "data-offset" attribute</p>

		<code>
			data-offset="120"
		</code>
	</li>

	<li>
		<p>Choose to run the animations on mobile devices (tablets and phones)</p>

		<code>
			mobileDisabled: true
		</code>
	</li>

	<li>
		<p>Choose the start point of the animation relatively to the viewport.</p>

		<code>
			offset: 0.8
		</code>

		<p>0.8 means that the animation will start when the top of the element is at 80% from the top of the viewport</p>

		<p>This number should be between 0 and 1.</p>
	</li>

	<li>
		<p>Choose whether to run the animation again as you scroll up and then down</p>

		<code>
			reverse: false
		</code>
	</li>
</ol>

<h2>Supported Browsers</h2>

<p>All browsers which know CSS transitions are supported.</p>

<p>IE9 and below will simply ignore the transitions and show the content as is.</p>

<p>Just remember to add all vendor prefixes, just in case :)</p>

<h2>Example setup:</h2>

<code>
	<pre>
		$(document).ready(function() {\n
			$('.animated').animated({
				animatedIn: 'animated-in',
				offset: 0.8,
				reverse: false,
				mobileDisabled: true
			});
		});
	</pre>
</code>