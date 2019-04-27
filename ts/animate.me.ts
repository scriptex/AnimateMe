interface AnimateMeOptions {
	offset?: number;
	reverse?: boolean;
	animatedIn?: string;
	offsetAttr?: string;
	animationAttr?: string;
	touchDisabled?: boolean;
}

export default class AnimateMe {
	private win: Window;
	private winO: number;
	private winW: number;
	private winH: number;
	private offsets: number[];
	private animated: Element[];
	private isTouchDevice: boolean;
	private options: AnimateMeOptions;
	private defaults: AnimateMeOptions = {
		offset: 0.5,
		reverse: true,
		animatedIn: 'animate-me--in',
		offsetAttr: 'data-offset',
		animationAttr: 'data-animation',
		touchDisabled: true
	};

	constructor(selector: string = '.animate-me', options: AnimateMeOptions = {}) {
		this.options = {
			...this.defaults,
			...options
		};
		this.win = window;
		this.offsets = [];
		// @ts-ignore
		this.animated = [...document.querySelectorAll(selector)];
		// prettier-ignore
		this.isTouchDevice = 'ontouchstart' in this.win || navigator.msMaxTouchPoints > 0  || navigator.maxTouchPoints > 0;

		if (this.options.offset > 1) {
			this.options.offset = 1;
		}

		if (this.options.offset < 0) {
			this.options.offset = 0;
		}

		this.getCurrentScroll();
		this.getWindowDimensions();

		this.scrollListener = this.scrollListener.bind(this);
		this.resizeListener = this.resizeListener.bind(this);

		this.start = this.start.bind(this);
		this.cleanup = this.cleanup.bind(this);
		this.destroy = this.destroy.bind(this);

		this.listen();
		this.start();

		return this;
	}

	start(): void {
		this.updateOffsets();
		this.bind();
	}

	listen(): void {
		this.win.addEventListener('animateme:enable', this.start, false);
		this.win.addEventListener('animateme:cleanup', this.cleanup, false);
		this.win.addEventListener('animateme:destroy', this.destroy, false);
	}

	getCurrentScroll(): void {
		this.winO = this.win.pageYOffset;
	}

	getWindowDimensions(): void {
		this.winH = this.win.innerHeight;
		this.winW = this.win.innerWidth;
	}

	scrollListener(): void {
		this.getCurrentScroll();
		this.animate();
	}

	resizeListener(): void {
		this.getWindowDimensions();
		this.updateOffsets();
	}

	bind(): void {
		this.getCurrentScroll();
		this.updateOffsets();
		this.animate();

		this.win.addEventListener('scroll', this.scrollListener, false);
		this.win.addEventListener('resize', this.resizeListener, false);
	}

	unbind(): void {
		this.win.removeEventListener('scroll', this.scrollListener, false);
		this.win.removeEventListener('resize', this.resizeListener, false);
	}

	cleanup(): void {
		this.animated.forEach((element: Element) => element.classList.remove(this.options.animatedIn));
	}

	destroy(): void {
		this.unbind();
		this.cleanup();
	}

	animate(): void {
		const app: AnimateMe = this;
		const opts: AnimateMeOptions = app.options;

		this.animated.forEach(
			(element: Element, i: number): void => {
				const animationName: string = element.getAttribute(opts.animationAttr) || '';

				if (opts.touchDisabled && app.isTouchDevice) {
					element.classList.add(opts.animatedIn);
				} else {
					const shouldAnimate: boolean = app.winO + app.winH * opts.offset > app.offsets[i];

					if (opts.reverse) {
						element.classList.toggle(opts.animatedIn, shouldAnimate);

						// prettier-ignore
						animationName && element.classList.toggle(animationName, shouldAnimate);
					} else {
						if (shouldAnimate) {
							element.classList.add(opts.animatedIn);

							animationName && element.classList.add(animationName);
						}
					}
				}
			}
		);
	}

	updateOffsets(): void {
		const app: AnimateMe = this;

		app.offsets = this.animated.map(
			(element: Element): number => {
				const elementOffset: number = element.getBoundingClientRect().top + app.win.pageYOffset;
				const offsetDelay: number = parseFloat(element.getAttribute(app.options.offsetAttr)) || 0;

				return elementOffset + offsetDelay;
			}
		);
	}
}
