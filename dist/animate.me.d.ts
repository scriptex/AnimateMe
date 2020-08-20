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
    private start;
    private listen;
    private getCurrentScroll;
    private getWindowDimensions;
    private scrollListener;
    private resizeListener;
    private bind;
    private unbind;
    private cleanup;
    private destroy;
    private animate;
    private updateOffsets;
}
export default AnimateMe;
