interface AnimateMeOptions {
    offset?: number;
    reverse?: boolean;
    animatedIn?: string;
    offsetAttr?: string;
    animationAttr?: string;
    touchDisabled?: boolean;
}
export default class AnimateMe {
    private win;
    private winO;
    private winW;
    private winH;
    private offsets;
    private animated;
    private isTouchDevice;
    private options;
    private defaults;
    constructor(selector?: string, options?: AnimateMeOptions);
    start(): void;
    listen(): void;
    getCurrentScroll(): void;
    getWindowDimensions(): void;
    scrollListener(): void;
    resizeListener(): void;
    bind(): void;
    unbind(): void;
    cleanup(): void;
    destroy(): void;
    animate(): void;
    updateOffsets(): void;
}
export {};
