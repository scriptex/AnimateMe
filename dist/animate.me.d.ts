export interface AnimateMeOptions {
    readonly offset: number;
    readonly reverse: boolean;
    readonly animatedIn: string;
    readonly offsetAttr: string;
    readonly animationAttr: string;
    readonly touchDisabled: boolean;
}
export declare class AnimateMe {
    options: AnimateMeOptions;
    animated: HTMLElement[];
    selector: string;
    private win;
    private winO;
    private winH;
    private offsets;
    private isTouchDevice;
    constructor(selector?: string, options?: Partial<AnimateMeOptions>);
    setCurrentScroll: () => void;
    setWindowDimensions: () => void;
    bind: () => void;
    unbind: () => void;
    cleanup: () => void;
    destroy: () => void;
    animate: () => void;
    setElements: () => void;
    updateOffsets: () => void;
    updateInstance: (shouldAnimate?: boolean) => void;
    private start;
    private listen;
    private scrollListener;
    private resizeListener;
}
export default AnimateMe;
