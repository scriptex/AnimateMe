"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __spreadArrays = (this && this.__spreadArrays) || function () {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
};
var AnimateMe = /** @class */ (function () {
    function AnimateMe(selector, options) {
        var _this = this;
        if (selector === void 0) { selector = '.animate-me'; }
        if (options === void 0) { options = {}; }
        this.win = window;
        this.winO = 0;
        this.winH = 0;
        this.winW = 0;
        this.offsets = [];
        this.options = {};
        this.animated = [];
        this.isTouchDevice = false;
        this.start = function () {
            _this.updateOffsets();
            _this.bind();
        };
        this.listen = function () {
            _this.win.addEventListener('animateme:enable', _this.start, false);
            _this.win.addEventListener('animateme:cleanup', _this.cleanup, false);
            _this.win.addEventListener('animateme:destroy', _this.destroy, false);
        };
        this.getCurrentScroll = function () {
            _this.winO = _this.win.pageYOffset;
        };
        this.getWindowDimensions = function () {
            _this.winH = _this.win.innerHeight;
            _this.winW = _this.win.innerWidth;
        };
        this.scrollListener = function () {
            _this.getCurrentScroll();
            _this.animate();
        };
        this.resizeListener = function () {
            _this.getWindowDimensions();
            _this.updateOffsets();
        };
        this.bind = function () {
            _this.getCurrentScroll();
            _this.updateOffsets();
            _this.animate();
            _this.win.addEventListener('scroll', _this.scrollListener, false);
            _this.win.addEventListener('resize', _this.resizeListener, false);
        };
        this.unbind = function () {
            _this.win.removeEventListener('scroll', _this.scrollListener, false);
            _this.win.removeEventListener('resize', _this.resizeListener, false);
        };
        this.cleanup = function () {
            _this.animated.forEach(function (element) { return element.classList.remove(_this.options.animatedIn); });
        };
        this.destroy = function () {
            _this.unbind();
            _this.cleanup();
        };
        this.animate = function () {
            var _a = _this, winO = _a.winO, winH = _a.winH, offsets = _a.offsets, _b = _a.options, offset = _b.offset, reverse = _b.reverse, animatedIn = _b.animatedIn, touchDisabled = _b.touchDisabled, animationAttr = _b.animationAttr, animated = _a.animated, isTouchDevice = _a.isTouchDevice;
            animated.forEach(function (element, i) {
                var animationName = element.getAttribute(animationAttr) || '';
                if (touchDisabled && isTouchDevice) {
                    element.classList.add(animatedIn);
                }
                else {
                    var shouldAnimate = winO + winH * offset > offsets[i];
                    if (reverse) {
                        element.classList.toggle(animatedIn, shouldAnimate);
                        // prettier-ignore
                        animationName && element.classList.toggle(animationName, shouldAnimate);
                    }
                    else {
                        if (shouldAnimate) {
                            element.classList.add(animatedIn);
                            animationName && element.classList.add(animationName);
                        }
                    }
                }
            });
        };
        this.updateOffsets = function () {
            var offsetAttr = _this.options.offsetAttr;
            var pageYOffset = _this.win.pageYOffset;
            _this.offsets = _this.animated.map(function (element) {
                var offsetDelay = parseFloat(element.getAttribute(offsetAttr)) || 0;
                var elementOffset = element.getBoundingClientRect().top + pageYOffset;
                return elementOffset + offsetDelay;
            });
        };
        this.options = __assign({ offset: 0.5, reverse: true, animatedIn: 'animate-me--in', offsetAttr: 'data-offset', animationAttr: 'data-animation', touchDisabled: true }, options);
        this.animated = __spreadArrays(document.querySelectorAll(selector));
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
    return AnimateMe;
}());
//# sourceMappingURL=animate.me.js.map