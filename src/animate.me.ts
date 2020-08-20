export interface AnimateMeOptions {
	offset?: number;
	readonly reverse?: boolean;
	readonly animatedIn?: string;
	readonly offsetAttr?: string;
	readonly animationAttr?: string;
	readonly touchDisabled?: boolean;
}

export class AnimateMe {
	private win: Window = window;
	private winO: number = 0;
	private winH: number = 0;
	private winW: number = 0;
	private offsets: number[] = [];
	private options: AnimateMeOptions = {};
	private animated: Element[] = [];
	private isTouchDevice: boolean = false;

	constructor(selector: string = '.animate-me', options: AnimateMeOptions = {}) {
		this.options = {
			offset: 0.5,
			reverse: true,
			animatedIn: 'animate-me--in',
			offsetAttr: 'data-offset',
			animationAttr: 'data-animation',
			touchDisabled: true,
			...options
		};

		this.animated = [...(document.querySelectorAll(selector) as any)];

		// prettier-ignore
		this.isTouchDevice = 'ontouchstart' in this.win || navigator.msMaxTouchPoints > 0 || navigator.maxTouchPoints > 0;

		if (this.options.offset && this.options.offset > 1) {
			this.options.offset = 1;
		}

		if (this.options.offset && this.options.offset < 0) {
			this.options.offset = 0;
		}

		this.getCurrentScroll();
		this.getWindowDimensions();

		this.listen();
		this.start();

		return this;
	}

	private start = (): void => {
		this.updateOffsets();
		this.bind();
	};

	private listen = (): void => {
		this.win.addEventListener('animateme:enable', this.start, false);
		this.win.addEventListener('animateme:cleanup', this.cleanup, false);
		this.win.addEventListener('animateme:destroy', this.destroy, false);
	};

	private getCurrentScroll = (): void => {
		this.winO = this.win.pageYOffset;
	};

	private getWindowDimensions = (): void => {
		this.winH = this.win.innerHeight;
		this.winW = this.win.innerWidth;
	};

	private scrollListener = (): void => {
		this.getCurrentScroll();
		this.animate();
	};

	private resizeListener = (): void => {
		this.getWindowDimensions();
		this.updateOffsets();
	};

	private bind = (): void => {
		this.getCurrentScroll();
		this.updateOffsets();
		this.animate();

		this.win.addEventListener('scroll', this.scrollListener, false);
		this.win.addEventListener('resize', this.resizeListener, false);
	};

	private unbind = (): void => {
		this.win.removeEventListener('scroll', this.scrollListener, false);
		this.win.removeEventListener('resize', this.resizeListener, false);
	};

	private cleanup = (): void => {
		this.animated.forEach((element: Element) => element.classList.remove(this.options.animatedIn!));
	};

	private destroy = (): void => {
		this.unbind();
		this.cleanup();
	};

	private animate = (): void => {
		const {
			winO,
			winH,
			offsets,
			options: { offset, reverse, animatedIn, touchDisabled, animationAttr },
			animated,
			isTouchDevice
		} = this;

		animated.forEach((element: Element, i: number): void => {
			const animationName = element.getAttribute(animationAttr!) || '';

			if (touchDisabled && isTouchDevice) {
				element.classList.add(animatedIn!);
			} else {
				const shouldAnimate = winO + winH * offset! > offsets[i];

				if (reverse) {
					element.classList.toggle(animatedIn!, shouldAnimate);

					// prettier-ignore
					animationName && element.classList.toggle(animationName, shouldAnimate);
				} else {
					if (shouldAnimate) {
						element.classList.add(animatedIn!);

						animationName && element.classList.add(animationName);
					}
				}
			}
		});
	};

	private updateOffsets = (): void => {
		const { offsetAttr } = this.options;
		const { pageYOffset } = this.win;

		this.offsets = this.animated.map((element: Element): number => {
			const offsetDelay = parseFloat(element.getAttribute(offsetAttr!)!) || 0;
			const elementOffset = element.getBoundingClientRect().top + pageYOffset;

			return elementOffset + offsetDelay;
		});
	};
}

export default AnimateMe;
