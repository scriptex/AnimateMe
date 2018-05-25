export default class AnimateMe {
  constructor(selector = '.animate-me', options = {}) {
    this.options = {
      offset: 0.5,
      reverse: true,
      animatedIn: 'animate-me--in',
      offsetAttr: 'data-offset',
      animationAttr: 'data-animation',
      touchDisabled: true,
      ...options
    };
    this.win = window;
    this.offsets = [];
    this.animated = document.querySelectorAll(selector);
    this.isTouchDevice =
      'ontouchstart' in this.win ||
      navigator.msMaxTouchPoints > 0 ||
      navigator.maxTouchPoints > 0;

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

    this.start();

    return this;
  }

  start() {
    this.updateOffsets();
    this.bind();
  }

  getCurrentScroll() {
    this.winO = this.win.pageYOffset;
  }

  getWindowDimensions() {
    this.winH = this.win.innerHeight;
    this.winW = this.win.innerWidth;
  }

  scrollListener() {
    this.getCurrentScroll();
    this.animate();
  }

  resizeListener() {
    this.getWindowDimensions();
    this.updateOffsets();
  }

  bind() {
    this.getCurrentScroll();
    this.updateOffsets();
    this.animate();

    this.win.addEventListener('scroll', this.scrollListener, false);
    this.win.addEventListener('resize', this.resizeListener, false);
  }

  unbind() {
    this.win.removeEventListener('scroll', this.scrollListener, false);
    this.win.removeEventListener('resize', this.resizeListener, false);
  }

  destroy() {
    this.unbind();

    [].forEach.call(this.animated, element => {
      element.classList.remove(this.options.animatedIn);
    });
  }

  animate() {
    const app = this;
    const opts = app.options;

    [].forEach.call(this.animated, (element, i) => {
      const animationName = element.getAttribute(opts.animationAttr) || '';

      if (opts.touchDisabled && app.isTouchDevice) {
        element.classList.add(opts.animatedIn);
      } else {
        const shouldAnimate =
          app.winO + app.winH * opts.offset > app.offsets[i];

        if (opts.reverse) {
          element.classList.toggle(opts.animatedIn, shouldAnimate);
          animationName &&
            element.classList.toggle(animationName, shouldAnimate);
        } else {
          if (shouldAnimate) {
            element.classList.add(opts.animatedIn);
            animationName && element.classList.add(animationName);
          }
        }
      }
    });
  }

  updateOffsets() {
    const app = this;

    app.offsets = [].map.call(app.animated, element => {
      const elementOffset =
        element.getBoundingClientRect().top + app.win.pageYOffset;
      const offsetDelay =
        parseFloat(element.getAttribute(app.options.offsetAttr)) || 0;

      return elementOffset + offsetDelay;
    });
  }
}
