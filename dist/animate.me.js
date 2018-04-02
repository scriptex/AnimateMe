"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

var AnimateMe =
/*#__PURE__*/
function () {
  function AnimateMe() {
    var selector = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : '.animate-me';
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

    _classCallCheck(this, AnimateMe);

    this.options = Object.assign({}, {
      offset: 0.5,
      reverse: true,
      animatedIn: 'animate-me--in',
      offsetAttr: 'data-offset',
      animationAttr: 'data-animation',
      touchDisabled: true
    }, options);
    this.win = window;
    this.offsets = [];
    this.animated = document.querySelectorAll(selector);
    this.isTouchDevice = 'ontouchstart' in this.win || navigator.msMaxTouchPoints > 0 || navigator.maxTouchPoints > 0;

    if (this.options.offset > 1) {
      this.options.offset = 1;
    }

    if (this.options.offset < 0) {
      this.options.offset = 0;
    }

    this.getCurrentScroll();
    this.getWindowDimensions();
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
    key: "bind",
    value: function bind() {
      var _this = this;

      this.getCurrentScroll();
      this.updateOffsets();
      this.animate();
      this.win.addEventListener('scroll', function () {
        _this.getCurrentScroll();

        _this.animate();
      }, false);
      this.win.addEventListener('resize', function () {
        _this.getWindowDimensions();

        _this.updateOffsets();
      }, false);
    }
  }, {
    key: "animate",
    value: function animate() {
      var app = this;
      var opts = app.options;
      [].forEach.call(this.animated, function (element, i) {
        var animationName = element.getAttribute(opts.animationAttr) || '';

        if (opts.touchDisabled && app.isTouchDevice) {
          element.classList.add(opts.animatedIn);
        } else {
          var shouldAnimate = app.winO + app.winH * opts.offset > app.offsets[i];

          if (opts.reverse) {
            element.classList.toggle(opts.animatedIn, shouldAnimate);
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
      app.offsets = [].map.call(app.animated, function (element) {
        var elementOffset = element.getBoundingClientRect().top + app.win.pageYOffset;
        var offsetDelay = parseFloat(element.getAttribute(app.options.offsetAttr)) || 0;
        return elementOffset + offsetDelay;
      });
    }
  }]);

  return AnimateMe;
}();

exports.default = AnimateMe;