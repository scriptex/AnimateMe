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
(function (factory) {
    if (typeof module === "object" && typeof module.exports === "object") {
        var v = factory(require, exports);
        if (v !== undefined) module.exports = v;
    }
    else if (typeof define === "function" && define.amd) {
        define(["require", "exports"], factory);
    }
})(function (require, exports) {
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.AnimateMe = void 0;
    var AnimateMe = /** @class */ (function () {
        function AnimateMe(selector, options) {
            var _this = this;
            if (selector === void 0) { selector = '.animate-me'; }
            if (options === void 0) { options = {}; }
            this.options = {
                offset: 0.5,
                reverse: true,
                animatedIn: 'animate-me--in',
                offsetAttr: 'data-offset',
                animationAttr: 'data-animation',
                touchDisabled: true
            };
            this.animated = [];
            this.selector = '.animate-me';
            this.win = window;
            this.winO = 0;
            this.winH = 0;
            this.offsets = [];
            this.isTouchDevice = false;
            this.setCurrentScroll = function () {
                _this.winO = _this.win.pageYOffset;
            };
            this.setWindowDimensions = function () {
                _this.winH = _this.win.innerHeight;
            };
            this.bind = function () {
                _this.setCurrentScroll();
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
                var offsetOption = offset > 1 ? 1 : offset < 0 ? 0 : offset;
                animated.forEach(function (element, i) {
                    var animationName = element.getAttribute(animationAttr) || '';
                    if (touchDisabled && isTouchDevice) {
                        element.classList.add(animatedIn);
                    }
                    else {
                        var shouldAnimate = winO + winH * offsetOption > offsets[i];
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
            this.setElements = function () {
                _this.animated = Array.from(document.querySelectorAll(_this.selector));
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
            this.updateInstance = function (shouldAnimate) {
                if (shouldAnimate === void 0) { shouldAnimate = false; }
                _this.setElements();
                _this.setWindowDimensions();
                _this.setCurrentScroll();
                _this.updateOffsets();
                if (shouldAnimate) {
                    _this.animate();
                }
            };
            this.start = function () {
                _this.updateOffsets();
                _this.bind();
            };
            this.listen = function () {
                _this.win.addEventListener('animateme:enable', _this.start, false);
                _this.win.addEventListener('animateme:cleanup', _this.cleanup, false);
                _this.win.addEventListener('animateme:destroy', _this.destroy, false);
            };
            this.scrollListener = function () {
                _this.setCurrentScroll();
                _this.animate();
            };
            this.resizeListener = function () {
                _this.setWindowDimensions();
                _this.updateOffsets();
            };
            this.selector = selector;
            this.options = __assign(__assign({}, this.options), options);
            this.setElements();
            this.isTouchDevice = 'ontouchstart' in this.win || navigator.maxTouchPoints > 0;
            this.setCurrentScroll();
            this.setWindowDimensions();
            this.listen();
            this.start();
            return this;
        }
        return AnimateMe;
    }());
    exports.AnimateMe = AnimateMe;
    exports.default = AnimateMe;
});
//# sourceMappingURL=animate.me.js.map