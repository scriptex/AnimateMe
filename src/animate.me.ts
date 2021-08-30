export interface AnimateMeOptions {
	readonly offset: number;
	readonly reverse: boolean;
	readonly animatedIn: string;
	readonly offsetAttr: string;
	readonly animationAttr: string;
	readonly touchDisabled: boolean;
}

export class AnimateMe {
	public options: AnimateMeOptions = {
		offset: 0.5,
		reverse: true,
		animatedIn: 'animate-me--in',
		offsetAttr: 'data-offset',
		animationAttr: 'data-animation',
		touchDisabled: true
	};
	public animated: HTMLElement[] = [];
	public selector = '.animate-me';

	private win: Window = window;
	private winO: number = 0;
	private winH: number = 0;
	private offsets: number[] = [];
	private isTouchDevice: boolean = false;

	constructor(selector: string = '.animate-me', options: Partial<AnimateMeOptions> = {}) {
		this.selector = selector;
		this.options = {
			...this.options,
			...options
		};

		this.setElements();

		this.isTouchDevice = 'ontouchstart' in this.win || navigator.maxTouchPoints > 0;

		this.setCurrentScroll();
		this.setWindowDimensions();

		this.listen();
		this.start();

		return this;
	}

	public setCurrentScroll = (): void => {
		this.winO = this.win.pageYOffset;
	};

	public setWindowDimensions = (): void => {
		this.winH = this.win.innerHeight;
	};

	public bind = (): void => {
		this.setCurrentScroll();
		this.updateOffsets();
		this.animate();

		this.win.addEventListener('scroll', this.scrollListener, false);
		this.win.addEventListener('resize', this.resizeListener, false);
	};

	public unbind = (): void => {
		this.win.removeEventListener('scroll', this.scrollListener, false);
		this.win.removeEventListener('resize', this.resizeListener, false);
	};

	public cleanup = (): void => {
		this.animated.forEach((element: Element) => element.classList.remove(this.options.animatedIn!));
	};

	public destroy = (): void => {
		this.unbind();
		this.cleanup();
	};

	public animate = (): void => {
		const {
			winO,
			winH,
			offsets,
			options: { offset, reverse, animatedIn, touchDisabled, animationAttr },
			animated,
			isTouchDevice
		} = this;

		const offsetOption = offset > 1 ? 1 : offset < 0 ? 0 : offset;

		animated.forEach((element: Element, i: number): void => {
			const animationName = element.getAttribute(animationAttr!) || '';

			if (touchDisabled && isTouchDevice) {
				element.classList.add(animatedIn!);
			} else {
				const shouldAnimate = winO + winH * offsetOption > offsets[i];

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

	public setElements = (): void => {
		this.animated = Array.from(document.querySelectorAll(this.selector));
	};

	public updateOffsets = (): void => {
		const { offsetAttr } = this.options;
		const { pageYOffset } = this.win;

		this.offsets = this.animated.map((element: Element): number => {
			const offsetDelay = parseFloat(element.getAttribute(offsetAttr!)!) || 0;
			const elementOffset = element.getBoundingClientRect().top + pageYOffset;

			return elementOffset + offsetDelay;
		});
	};

	public updateInstance = (shouldAnimate = false): void => {
		this.setElements();
		this.setWindowDimensions();
		this.setCurrentScroll();
		this.updateOffsets();

		if (shouldAnimate) {
			this.animate();
		}
	};

	private start = (): void => {
		this.updateOffsets();
		this.bind();
	};

	private listen = (): void => {
		this.win.addEventListener('animateme:enable', this.start, false);
		this.win.addEventListener('animateme:cleanup', this.cleanup, false);
		this.win.addEventListener('animateme:destroy', this.destroy, false);
	};

	private scrollListener = (): void => {
		this.setCurrentScroll();
		this.animate();
	};

	private resizeListener = (): void => {
		this.setWindowDimensions();
		this.updateOffsets();
	};
}

export default AnimateMe;
