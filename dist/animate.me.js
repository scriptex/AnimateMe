(function (global, factory) {
  if (typeof define === "function" && define.amd) {
    define(["exports"], factory);
  } else if (typeof exports !== "undefined") {
    factory(exports);
  } else {
    var mod = {
      exports: {}
    };
    factory(mod.exports);
    global.animateMe = mod.exports;
  }
})(typeof globalThis !== "undefined" ? globalThis : typeof self !== "undefined" ? self : this, function (_exports) {
  "use strict";

  Object.defineProperty(_exports, "__esModule", {
    value: true
  });
  _exports["default"] = void 0;

  function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

  function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

  function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

  function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

  function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

  function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

  function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

  function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

  function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

  function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

  function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

  function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

  var AnimateMe = /*#__PURE__*/function () {
    function AnimateMe() {
      var selector = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : '.animate-me';
      var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

      _classCallCheck(this, AnimateMe);

      this.options = _objectSpread({
        offset: 0.5,
        reverse: true,
        animatedIn: 'animate-me--in',
        offsetAttr: 'data-offset',
        animationAttr: 'data-animation',
        touchDisabled: true
      }, options);
      this.win = window;
      this.offsets = [];
      this.animated = _toConsumableArray(document.querySelectorAll(selector));
      this.isTouchDevice = 'ontouchstart' in this.win || navigator.msMaxTouchPoints > 0 || navigator.maxTouchPoints > 0;

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

    _createClass(AnimateMe, [{
      key: "start",
      value: function start() {
        this.updateOffsets();
        this.bind();
      }
    }, {
      key: "listen",
      value: function listen() {
        this.win.addEventListener('animateme:enable', this.start, false);
        this.win.addEventListener('animateme:cleanup', this.cleanup, false);
        this.win.addEventListener('animateme:destroy', this.destroy, false);
      }
    }, {
      key: "getCurrentScroll",
      value: function getCurrentScroll() {
        this.winO = this.win.pageYOffset;
      }
    }, {
      key: "getWindowDimensions",
      value: function getWindowDimensions() {
        this.winH = this.win.innerHeight;
        this.winW = this.win.innerWidth;
      }
    }, {
      key: "scrollListener",
      value: function scrollListener() {
        this.getCurrentScroll();
        this.animate();
      }
    }, {
      key: "resizeListener",
      value: function resizeListener() {
        this.getWindowDimensions();
        this.updateOffsets();
      }
    }, {
      key: "bind",
      value: function bind() {
        this.getCurrentScroll();
        this.updateOffsets();
        this.animate();
        this.win.addEventListener('scroll', this.scrollListener, false);
        this.win.addEventListener('resize', this.resizeListener, false);
      }
    }, {
      key: "unbind",
      value: function unbind() {
        this.win.removeEventListener('scroll', this.scrollListener, false);
        this.win.removeEventListener('resize', this.resizeListener, false);
      }
    }, {
      key: "cleanup",
      value: function cleanup() {
        var _this = this;

        // prettier-ignore
        this.animated.forEach(function (element) {
          return element.classList.remove(_this.options.animatedIn);
        });
      }
    }, {
      key: "destroy",
      value: function destroy() {
        this.unbind();
        this.cleanup();
      }
    }, {
      key: "animate",
      value: function animate() {
        var app = this;
        var opts = app.options;
        this.animated.forEach(function (element, i) {
          var animationName = element.getAttribute(opts.animationAttr) || '';

          if (opts.touchDisabled && app.isTouchDevice) {
            element.classList.add(opts.animatedIn);
          } else {
            var shouldAnimate = app.winO + app.winH * opts.offset > app.offsets[i];

            if (opts.reverse) {
              element.classList.toggle(opts.animatedIn, shouldAnimate); // prettier-ignore

              animationName && element.classList.toggle(animationName, shouldAnimate);
            } else {
              if (shouldAnimate) {
                element.classList.add(opts.animatedIn);
                animationName && element.classList.add(animationName);
              }
            }
          }
        });
      }
    }, {
      key: "updateOffsets",
      value: function updateOffsets() {
        var app = this;
        app.offsets = this.animated.map(function (element) {
          // prettier-ignore
          var elementOffset = element.getBoundingClientRect().top + app.win.pageYOffset; // prettier-ignore

          var offsetDelay = parseFloat(element.getAttribute(app.options.offsetAttr)) || 0;
          return elementOffset + offsetDelay;
        });
      }
    }]);

    return AnimateMe;
  }();

  _exports["default"] = AnimateMe;
});
