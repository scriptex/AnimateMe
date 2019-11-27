export interface AnimateMeOptions {
    offset?: number;
    readonly reverse?: boolean;
    readonly animatedIn?: string;
    readonly offsetAttr?: string;
    readonly animationAttr?: string;
    readonly touchDisabled?: boolean;
}
export declare class AnimateMe {
    private win;
    private winO;
    private winH;
    private winW;
    private offsets;
    private options;
    private animated;
    private isTouchDevice;
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
export default AnimateMe;
