(() => {
    var __webpack_modules__ = {
            926: e => {
                e.exports = {
                    SMALL_WIDTH: "mediaSmallWidth",
                    MEDIUM_WIDTH: "mediaMediumWidth",
                    LARGE_WIDTH: "mediaLargeWidth",
                    EXTRA_LARGE_WIDTH: "mediaExtraLargeWidth",
                    SMALL_HEIGHT: "mediaSmallHeight",
                    MEDIUM_HEIGHT: "mediaMediumHeight",
                    LARGE_HEIGHT: "mediaLargeHeight",
                    EXTRA_LARGE_HEIGHT: "mediaExtraLargeHeight",
                    SMALL: "mediaSmall",
                    MEDIUM: "mediaMedium",
                    LARGE: "mediaLarge",
                    EXTRA_LARGE: "mediaExtraLarge"
                }
            },
            527: (e, u, t) => {
                "use strict";
                t.r(u), t.d(u, {
                    mouse: () => c,
                    off: () => o,
                    on: () => s,
                    onResize: () => r,
                    onScaleUpdated: () => i
                });
                var a = t(2472),
                    n = t(1176);
                const r = (0, a.E)("clientResized"),
                    i = (0, a.E)("self.onScaleUpdated"),
                    s = (e, u) => engine.on(e, u),
                    o = (e, u) => engine.off(e, u),
                    l = {
                        down: (0, a.E)("mousedown"),
                        up: (0, a.E)("mouseup"),
                        move: (0, a.E)("mousemove")
                    };
                const c = function() {
                    const e = {
                        listeners: 0,
                        enabled: !0,
                        initialized: !1
                    };

                    function u() {
                        e.enabled && (0, n.R)(!1)
                    }

                    function t() {
                        e.enabled && (0, n.R)(!0)
                    }

                    function a() {
                        e.enabled ? e.listeners < 1 ? (e.initialized = !1, document.body.removeEventListener("mouseenter", u), document.body.removeEventListener("mouseleave", t)) : e.initialized || (e.initialized = !0, document.body.addEventListener("mouseenter", u), document.body.addEventListener("mouseleave", t)) : (0, n.R)(!1)
                    }
                    const r = ["down", "up", "move"].reduce(((u, t) => (u[t] = function(u) {
                        return t => {
                            e.listeners += 1;
                            let n = !0;
                            const r = `mouse${u}`,
                                i = l[u]((e => t([e, "outside"])));

                            function s(e) {
                                t([e, "inside"])
                            }
                            return window.addEventListener(r, s), a(), () => {
                                n && (i(), window.removeEventListener(r, s), e.listeners -= 1, a(), n = !1)
                            }
                        }
                    }(t), u)), {});
                    return Object.assign({}, r, {
                        disable() {
                            e.enabled = !1, a()
                        },
                        enable() {
                            e.enabled = !0, a()
                        },
                        enableOutside() {
                            e.enabled && (0, n.R)(!0)
                        },
                        disableOutside() {
                            e.enabled && (0, n.R)(!1)
                        }
                    })
                }()
            },
            5959: (e, u, t) => {
                "use strict";
                t.r(u), t.d(u, {
                    events: () => a,
                    getMouseGlobalPosition: () => i,
                    getSize: () => r,
                    graphicsQuality: () => s,
                    playSound: () => n.G,
                    setRTPC: () => n.E
                });
                var a = t(527),
                    n = t(2493);

                function r(e = "px") {
                    return "rem" === e ? viewEnv.getClientSizeRem() : viewEnv.getClientSizePx()
                }

                function i(e = "px") {
                    return "rem" === e ? viewEnv.getMouseGlobalPositionRem() : viewEnv.getMouseGlobalPositionPx()
                }
                const s = {
                    isLow: () => 1 === viewEnv.getGraphicsQuality(),
                    isHigh: () => 0 === viewEnv.getGraphicsQuality(),
                    get: () => viewEnv.getGraphicsQuality()
                }
            },
            1176: (e, u, t) => {
                "use strict";

                function a(e) {
                    viewEnv.setTrackMouseOnStage(e)
                }
                t.d(u, {
                    R: () => a
                })
            },
            2493: (e, u, t) => {
                "use strict";

                function a(e) {
                    engine.call("PlaySound", e).catch((u => {
                        console.error(`playSound('${e}'): `, u)
                    }))
                }

                function n(e, u) {
                    engine.call("SetRTPCGlobal", e, u).catch((t => {
                        console.error(`setRTPC('${e}', '${u}'): `, t)
                    }))
                }
                t.d(u, {
                    E: () => n,
                    G: () => a
                })
            },
            2472: (e, u, t) => {
                "use strict";

                function a(e) {
                    return u => (engine.on(e, u), () => {
                        engine.off(e, u)
                    })
                }
                t.d(u, {
                    E: () => a
                })
            },
            3138: (e, u, t) => {
                "use strict";
                t.d(u, {
                    O: () => r
                });
                var a = t(5959),
                    n = t(514);
                const r = {
                    view: t(7641),
                    client: a,
                    sound: n.ZP
                }
            },
            514: (e, u, t) => {
                "use strict";
                t.d(u, {
                    ZP: () => i
                });
                var a = t(5959);
                const n = {
                        highlight: "highlight",
                        click: "play",
                        yes1: "yes1"
                    },
                    r = Object.keys(n).reduce(((e, u) => (e[u] = () => (0, a.playSound)(n[u]), e)), {}),
                    i = {
                        play: Object.assign({}, r, {
                            sound: a.playSound
                        }),
                        setRTPC: a.setRTPC
                    }
            },
            3722: (e, u, t) => {
                "use strict";

                function a(e, u, t = 1) {
                    return viewEnv.getChildTexturePath(e, u.width, u.height, t)
                }

                function n(e, u, t) {
                    return `url(${a(e,u,t)})`
                }
                t.r(u), t.d(u, {
                    getBgUrl: () => n,
                    getTextureUrl: () => a
                })
            },
            6112: (e, u, t) => {
                "use strict";
                t.d(u, {
                    W: () => a
                });
                const a = {
                    showing: 0,
                    shown: 1,
                    hiding: 2,
                    hidden: 3
                }
            },
            6538: (e, u, t) => {
                "use strict";
                t.d(u, {
                    U: () => n
                });
                var a = t(2472);
                const n = {
                    onTextureFrozen: (0, a.E)("self.onTextureFrozen"),
                    onTextureReady: (0, a.E)("self.onTextureReady"),
                    onDomBuilt: (0, a.E)("self.onDomBuilt"),
                    onLoaded: (0, a.E)("self.onLoaded"),
                    onDisplayChanged: (0, a.E)("self.onShowingStatusChanged"),
                    onFocusUpdated: (0, a.E)("self.onFocusChanged"),
                    children: {
                        onAdded: (0, a.E)("children.onAdded"),
                        onLoaded: (0, a.E)("children.onLoaded"),
                        onRemoved: (0, a.E)("children.onRemoved"),
                        onAttached: (0, a.E)("children.onAttached"),
                        onTextureReady: (0, a.E)("children.onTextureReady"),
                        onRequestPosition: (0, a.E)("children.requestPosition")
                    }
                }
            },
            7641: (e, u, t) => {
                "use strict";
                t.r(u), t.d(u, {
                    addModelObserver: () => d,
                    addPreloadTexture: () => o,
                    arabic2roman: () => w,
                    children: () => n,
                    displayStatus: () => r.W,
                    displayStatusIs: () => x,
                    events: () => i.U,
                    extraSize: () => S,
                    forceTriggerMouseMove: () => b,
                    freezeTextureBeforeResize: () => F,
                    getBrowserTexturePath: () => c,
                    getDisplayStatus: () => h,
                    getFontNames: () => y,
                    getScale: () => g,
                    getSize: () => _,
                    getViewGlobalPosition: () => A,
                    isEventHandled: () => f,
                    isFocused: () => B,
                    pxToRem: () => D,
                    remToPx: () => C,
                    resize: () => E,
                    sendEvent: () => s.qP,
                    setAnimateWindow: () => v,
                    setEventHandled: () => p,
                    setInputPaddingsRem: () => l,
                    setSidePaddingsRem: () => m,
                    whenTutorialReady: () => L
                });
                var a = t(9690),
                    n = t(3722),
                    r = t(6112),
                    i = t(6538),
                    s = t(8566);

                function o(e) {
                    viewEnv.addPreloadTexture(e)
                }

                function l(e) {
                    viewEnv.setHitAreaPaddingsRem(e, e, e, e, 15)
                }

                function c(e, u, t, a = 1) {
                    return viewEnv.getWebBrowserTexturePath(e, u, t, a)
                }

                function d(e, u, t) {
                    return viewEnv.addDataChangedCallback(e, u, t)
                }

                function m(e) {
                    viewEnv.setHitAreaPaddingsRem(e.top, e.right, e.bottom, e.left, 15)
                }

                function _(e = "px") {
                    return "rem" === e ? viewEnv.getViewSizeRem() : viewEnv.getViewSizePx()
                }

                function E(e, u, t = "px") {
                    return "rem" === t ? viewEnv.resizeViewRem(e, u) : viewEnv.resizeViewPx(e, u)
                }

                function A(e = "rem") {
                    const u = viewEnv.getViewGlobalPositionRem();
                    return "rem" === e ? u : {
                        x: C(u.x),
                        y: C(u.y)
                    }
                }

                function F() {
                    viewEnv.freezeTextureBeforeResize()
                }

                function g() {
                    return viewEnv.getScale()
                }

                function D(e) {
                    return viewEnv.pxToRem(e)
                }

                function C(e) {
                    return viewEnv.remToPx(e)
                }

                function v(e, u) {
                    viewEnv.setAnimateWindow(e, u)
                }

                function B() {
                    return viewEnv.isFocused()
                }

                function p() {
                    return viewEnv.setEventHandled()
                }

                function f() {
                    return viewEnv.isEventHandled()
                }

                function b() {
                    viewEnv.forceTriggerMouseMove()
                }

                function h() {
                    return viewEnv.getShowingStatus()
                }
                const y = (() => {
                        let e = [];
                        return () => (0 === e.length && (e = Object.keys(viewEnv.getFontsConfig())), e)
                    })(),
                    w = a.cg,
                    x = Object.keys(r.W).reduce(((e, u) => (e[u] = () => viewEnv.getShowingStatus() === r.W[u], e)), {}),
                    S = {
                        set: (e, u) => {
                            viewEnv.setExtraSizeRem(e, u)
                        },
                        get: (e, u) => {
                            viewEnv.getExtraSizeRem(e, u)
                        }
                    },
                    L = Promise.all([new Promise((e => {
                        window.isDomBuilt ? e() : i.U.onDomBuilt(e)
                    })), engine.whenReady])
            },
            8566: (e, u, t) => {
                "use strict";
                t.d(u, {
                    qP: () => l
                });
                const a = ["args"];
                const n = 2,
                    r = 16,
                    i = 32,
                    s = 64,
                    o = (e, u) => {
                        const t = "GFViewEventProxy";
                        if (void 0 !== u) {
                            const r = u.args,
                                i = function(e, u) {
                                    if (null == e) return {};
                                    var t, a, n = {},
                                        r = Object.keys(e);
                                    for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                                    return n
                                }(u, a);
                            return void 0 !== r ? viewEnv.handleViewEvent(Object.assign({
                                __Type: t,
                                type: e
                            }, i, {
                                arguments: (n = r, Object.entries(n).map((([e, u]) => {
                                    const t = "GFValueProxy";
                                    switch (typeof u) {
                                        case "number":
                                            return {
                                                __Type: t, name: e, number: u
                                            };
                                        case "boolean":
                                            return {
                                                __Type: t, name: e, bool: u
                                            };
                                        default:
                                            return {
                                                __Type: t, name: e, string: u.toString()
                                            }
                                    }
                                })))
                            })) : viewEnv.handleViewEvent(Object.assign({
                                __Type: t,
                                type: e
                            }, i))
                        }
                        return viewEnv.handleViewEvent({
                            __Type: t,
                            type: e
                        });
                        var n
                    },
                    l = {
                        close(e) {
                            o("popover" === e ? n : i)
                        },
                        minimize() {
                            o(s)
                        },
                        move(e) {
                            o(r, {
                                isMouseEvent: !0,
                                on: e
                            })
                        }
                    }
            },
            5521: (e, u, t) => {
                "use strict";
                let a, n;
                t.d(u, {
                        n: () => a
                    }),
                    function(e) {
                        e[e.NONE = -1] = "NONE", e[e.ALT = 165] = "ALT", e[e.ENTER = 13] = "ENTER", e[e.ESCAPE = 27] = "ESCAPE", e[e.SPACE = 32] = "SPACE", e[e.END = 35] = "END", e[e.HOME = 36] = "HOME", e[e.ARROW_LEFT = 37] = "ARROW_LEFT", e[e.ARROW_UP = 38] = "ARROW_UP", e[e.ARROW_RIGHT = 39] = "ARROW_RIGHT", e[e.ARROW_DOWN = 40] = "ARROW_DOWN", e[e.NUM_PLUS = 107] = "NUM_PLUS", e[e.NUM_MINUS = 109] = "NUM_MINUS", e[e.PLUS = 187] = "PLUS", e[e.MINUS = 189] = "MINUS", e[e.PAGE_UP = 33] = "PAGE_UP", e[e.PAGE_DOWN = 34] = "PAGE_DOWN", e[e.BACKSPACE = 8] = "BACKSPACE", e[e.DELETE = 46] = "DELETE", e[e.TAB = 9] = "TAB", e[e.KEY_N = 78] = "KEY_N", e[e.KEY_1 = 49] = "KEY_1", e[e.KEY_2 = 50] = "KEY_2", e[e.KEY_3 = 51] = "KEY_3", e[e.KEY_4 = 52] = "KEY_4", e[e.KEY_5 = 53] = "KEY_5", e[e.KEY_6 = 54] = "KEY_6", e[e.KEY_7 = 55] = "KEY_7", e[e.KEY_8 = 56] = "KEY_8", e[e.KEY_9 = 57] = "KEY_9"
                    }(a || (a = {})),
                    function(e) {
                        e.ALT = "Alt", e.ALT_GRAPH = "AltGraph", e.CAPS_LOCK = "CapsLock", e.CONTROL = "Control", e.FN = "Fn", e.FN_LOCK = "FnLock", e.META = "Meta", e.NUM_LOCK = "NumLock", e.SCROLL_LOCK = "ScrollLock", e.SHIFT = "Shift", e.SYMBOL = "Symbol", e.SYMBOL_LOCK = "SymbolLock"
                    }(n || (n = {}))
            },
            9690: (e, u, t) => {
                "use strict";
                t.d(u, {
                    cg: () => r
                });
                const a = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"],
                    n = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1e3];

                function r(e) {
                    let u = "";
                    for (let t = n.length - 1; t >= 0; t--)
                        for (; e >= n[t];) u += a[t], e -= n[t];
                    return u
                } ["ko", "no"].includes(R.strings.settings.LANGUAGE_CODE())
            },
            1358: (e, u, t) => {
                "use strict";
                t.d(u, {
                    Z: () => r
                });
                var a = t(3138);
                class n {
                    constructor() {
                        this._callbacks = void 0, this._updateHandler = void 0, this._views = void 0, this.clearViewCallbacks = e => {
                            this._views[e] && (this._views[e].forEach((e => {
                                delete this._callbacks[e]
                            })), delete this._views[e])
                        }, this._callbacks = {}, this._views = {}, this._updateHandler = void 0
                    }
                    static get instance() {
                        return window.__dataTracker || (window.__dataTracker = new n), window.__dataTracker
                    }
                    clear() {
                        void 0 !== this._updateHandler && (this._updateHandler.clear(), this._updateHandler = void 0), this._callbacks = {}
                    }
                    addCallback(e, u, t = 0, n = !0) {
                        void 0 === this._updateHandler && (this._updateHandler = engine.on("viewEnv.onDataChanged", this._emmitDataChanged, this));
                        const r = a.O.view.addModelObserver(e, t, n);
                        return r > 0 ? (this._callbacks[r] = u, t > 0 && (this._views[t] ? this._views[t].push(r) : this._views[t] = [r])) : console.error("Can't add callback for model:", e), r
                    }
                    removeCallback(e, u = 0) {
                        let t = !1;
                        return void 0 !== e && void 0 !== this._callbacks[e] && (t = viewEnv.removeDataChangedCallback(e, u), delete this._callbacks[e]), t || console.error("Can't remove callback by id:", e), t
                    }
                    _emmitDataChanged(e, u, t) {
                        t.forEach((t => {
                            const a = this._callbacks[t];
                            void 0 !== a && a(e, u)
                        }))
                    }
                }
                n.__instance = void 0;
                const r = n
            },
            7572: (__unused_webpack_module, __webpack_exports__, __webpack_require__) => {
                "use strict";
                __webpack_require__.d(__webpack_exports__, {
                    Z: () => __WEBPACK_DEFAULT_EXPORT__
                });
                var _DataTracker__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(1358),
                    _index__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(9916);
                class ViewModel {
                    constructor(path, watchingFields = []) {
                        this.dataTracker = void 0, this.modelPath = void 0, this.callbacks = void 0, this.data = void 0, this._notifyObservers = () => {
                            this.data = eval(this.modelPath), this.callbacks.forEach((e => {
                                e(this.data)
                            }))
                        }, this.dataTracker = new _DataTracker__WEBPACK_IMPORTED_MODULE_0__.Z, this.modelPath = path, this.callbacks = new Set, (0, _index__WEBPACK_IMPORTED_MODULE_1__.ry)().then((() => {
                            this._addCallback(path), watchingFields.forEach((e => {
                                this._addCallback(path + "." + e)
                            })), this._notifyObservers()
                        }))
                    }
                    subscribe(e) {
                        this.callbacks.add(e), null !== this.data && void 0 !== this.data && e(this.data)
                    }
                    unsubscribe(e) {
                        this.callbacks.delete(e)
                    }
                    destroy() {
                        this.dataTracker.clear(), this.callbacks.clear()
                    }
                    _addCallback(e) {
                        this.dataTracker.addCallback(e, this._notifyObservers)
                    }
                }
                const __WEBPACK_DEFAULT_EXPORT__ = ViewModel
            },
            9916: (e, u, t) => {
                "use strict";
                t.d(u, {
                    Sw: () => r.Z,
                    B3: () => o,
                    Z5: () => i.Z5,
                    B0: () => s,
                    ry: () => g
                });
                class a {
                    constructor() {
                        this.entries = [], this._listenMouse = !1, this.onMouseDown = e => {
                            this.entries.forEach((({
                                container: u,
                                callback: t
                            }) => {
                                let a = e.target;
                                do {
                                    if (a === u) return;
                                    a = a.parentNode
                                } while (a);
                                t()
                            }))
                        }
                    }
                    static get instance() {
                        return a.__instance || (a.__instance = new a), a.__instance
                    }
                    register(e, u) {
                        this.addMouseListener(), this.entries.push({
                            container: e,
                            callback: u
                        })
                    }
                    unregister(e, u) {
                        const t = e,
                            a = u;
                        this.entries = this.entries.filter((({
                            container: e,
                            callback: u
                        }) => e !== t || u !== a)), this.removeMouseListener()
                    }
                    addMouseListener() {
                        this._listenMouse || (document.addEventListener("mousedown", this.onMouseDown), this._listenMouse = !0)
                    }
                    removeMouseListener() {
                        this._listenMouse && 0 === this.entries.length && (document.removeEventListener("mousedown", this.onMouseDown), this._listenMouse = !1)
                    }
                }
                a.__instance = void 0;
                const n = a;
                var r = t(1358);
                var i = t(8613);
                let s;
                ! function(e) {
                    e[e.UNDEFINED = 0] = "UNDEFINED", e[e.TOOLTIP = 1] = "TOOLTIP", e[e.POP_OVER = 2] = "POP_OVER", e[e.CONTEXT_MENU = 4] = "CONTEXT_MENU", e[e.DROP_DOWN = 8] = "DROP_DOWN", e[e.MOVE = 16] = "MOVE", e[e.CLOSE = 32] = "CLOSE", e[e.MINIMIZE = 64] = "MINIMIZE"
                }(s || (s = {}));
                const o = Object.freeze({
                        INTEGRAL: 0,
                        GOLD: 1
                    }),
                    l = Object.freeze({
                        FRACTIONAL: 0,
                        WO_ZERO_DIGITS: 1
                    }),
                    c = Object.freeze({
                        SHORT_FORMAT: 0,
                        LONG_FORMAT: 1
                    }),
                    d = Object.freeze({
                        SHORT_FORMAT: 0,
                        LONG_FORMAT: 1,
                        YEAR_MONTH: 2
                    });
                var m = t(5521),
                    _ = t(3138);
                const E = ["args"];

                function A(e, u, t, a, n, r, i) {
                    try {
                        var s = e[r](i),
                            o = s.value
                    } catch (e) {
                        return void t(e)
                    }
                    s.done ? u(o) : Promise.resolve(o).then(a, n)
                }
                const F = e => ({
                        __Type: "GFBoundingBox",
                        x: e.x,
                        y: e.y,
                        width: e.width,
                        height: e.height
                    }),
                    g = function() {
                        var e, u = (e = function*() {
                            return !(!engine._BindingsReady || !engine._WindowLoaded) || new Promise((e => {
                                engine.on("Ready", e)
                            }))
                        }, function() {
                            var u = this,
                                t = arguments;
                            return new Promise((function(a, n) {
                                var r = e.apply(u, t);

                                function i(e) {
                                    A(r, a, n, i, s, "next", e)
                                }

                                function s(e) {
                                    A(r, a, n, i, s, "throw", e)
                                }
                                i(void 0)
                            }))
                        });
                        return function() {
                            return u.apply(this, arguments)
                        }
                    }(),
                    D = (e, u) => {
                        const t = "GFViewEventProxy";
                        if (void 0 !== u) {
                            const n = u.args,
                                r = function(e, u) {
                                    if (null == e) return {};
                                    var t, a, n = {},
                                        r = Object.keys(e);
                                    for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                                    return n
                                }(u, E);
                            void 0 !== n ? viewEnv.handleViewEvent(Object.assign({
                                __Type: t,
                                type: e
                            }, r, {
                                arguments: (a = n, Object.entries(a).map((([e, u]) => {
                                    const t = {
                                        __Type: "GFValueProxy",
                                        name: e
                                    };
                                    switch (typeof u) {
                                        case "number":
                                            t.number = u;
                                            break;
                                        case "boolean":
                                            t.bool = u;
                                            break;
                                        default:
                                            t.string = u.toString()
                                    }
                                    return t
                                })))
                            })) : viewEnv.handleViewEvent(Object.assign({
                                __Type: t,
                                type: e
                            }, r))
                        } else viewEnv.handleViewEvent({
                            __Type: t,
                            type: e
                        });
                        var a
                    },
                    C = () => D(s.CLOSE),
                    v = (e, u) => {
                        e.keyCode === m.n.ESCAPE && u()
                    };
                var B = t(7572);
                const p = n.instance,
                    f = {
                        DataTracker: r.Z,
                        ViewModel: B.Z,
                        ViewEventType: s,
                        NumberFormatType: o,
                        RealFormatType: l,
                        TimeFormatType: c,
                        DateFormatType: d,
                        makeGlobalBoundingBox: F,
                        sendMoveEvent: e => D(s.MOVE, {
                            isMouseEvent: !0,
                            on: e
                        }),
                        sendCloseEvent: C,
                        sendClosePopOverEvent: () => D(s.POP_OVER, {
                            on: !1
                        }),
                        sendShowContextMenuEvent: (e, u, t = 0) => {
                            D(s.CONTEXT_MENU, {
                                isMouseEvent: !0,
                                contentID: e,
                                on: !0,
                                decoratorID: t,
                                args: u
                            })
                        },
                        sendShowPopOverEvent: (e, u, t, a, n = R.invalid("resId"), r) => {
                            const i = _.O.view.getViewGlobalPosition(),
                                o = t.getBoundingClientRect(),
                                l = o.x,
                                c = o.y,
                                d = o.width,
                                m = o.height,
                                E = {
                                    x: _.O.view.pxToRem(l) + i.x,
                                    y: _.O.view.pxToRem(c) + i.y,
                                    width: _.O.view.pxToRem(d),
                                    height: _.O.view.pxToRem(m)
                                };
                            D(s.POP_OVER, {
                                isMouseEvent: !0,
                                contentID: e,
                                decoratorID: a || R.invalid("resId"),
                                targetID: n,
                                direction: u,
                                bbox: F(E),
                                on: !0,
                                args: r
                            })
                        },
                        addEscapeListener: e => {
                            const u = u => v(u, e);
                            return window.addEventListener("keydown", u), () => window.removeEventListener("keydown", u)
                        },
                        closeOnEsc: e => {
                            v(e, C)
                        },
                        handleViewEvent: D,
                        onBindingsReady: g,
                        onLayoutReady: () => new Promise((e => {
                            requestAnimationFrame((() => {
                                requestAnimationFrame((() => {
                                    e()
                                }))
                            }))
                        })),
                        isTooltipShown: () => viewEnv.isWindowShownByViewEvent(s.TOOLTIP),
                        isContextMenuShown: () => viewEnv.isWindowShownByViewEvent(s.CONTEXT_MENU),
                        isPopOverShown: () => viewEnv.isWindowShownByViewEvent(s.POP_OVER),
                        dumpViewModel: function e(u) {
                            const t = {};
                            if ("object" != typeof u) return u;
                            for (const a in u)
                                if (Object.prototype.hasOwnProperty.call(u, a)) {
                                    const n = Object.prototype.toString.call(u[a]);
                                    if (n.startsWith("[object CoherentArrayProxy]")) {
                                        const n = u[a];
                                        t[a] = [];
                                        for (let u = 0; u < n.length; u++) t[a].push({
                                            value: e(n[u].value)
                                        })
                                    } else n.startsWith("[object class BW::WULF::ViewModel") ? t[a] = e(u[a]) : t[a] = u[a]
                                } return t
                        },
                        ClickOutsideManager: p,
                        SystemLocale: i.Z5,
                        UserLocale: i.cy
                    };
                window.ViewEnvHelper = f
            },
            8613: (e, u, t) => {
                "use strict";
                t.d(u, {
                    Ew: () => r,
                    Z5: () => a,
                    cy: () => n
                });
                const a = {
                        getNumberFormat: (e, u) => systemLocale.getNumberFormat(e, u),
                        getRealFormat: (e, u) => systemLocale.getRealFormat(e, u),
                        getTimeFormat: (e, u) => systemLocale.getTimeFormat(e, u),
                        getDateFormat: (e, u) => systemLocale.getDateFormat(e, u),
                        toUpperCase: e => systemLocale.toUpperCase(e),
                        toLowerCase: e => systemLocale.toUpperCase(e)
                    },
                    n = {
                        getNumberFormat: e => userLocale.getNumberFormat(e),
                        getTimeFormat: (e, u, t) => userLocale.getTimeFormat(e, u, void 0 === t || t),
                        getTimeString: (e, u, t) => userLocale.getTimeString(e, u, void 0 === t || t)
                    },
                    r = {
                        getRegionalDateTime: (e, u, t = !0) => regionalDateTime.getRegionalDateTime(e, u, t),
                        getFormattedDateTime: (e, u, t = !0) => regionalDateTime.getFormattedDateTime(e, u, t)
                    }
            },
            5705: (e, u, t) => {
                "use strict";
                var a = {};
                t.r(a), t.d(a, {
                    Area: () => Se,
                    Bar: () => ye,
                    DefaultScroll: () => xe,
                    Direction: () => ce,
                    defaultSettings: () => de,
                    useHorizontalScrollApi: () => _e
                });
                var n = {};
                t.r(n), t.d(n, {
                    Area: () => Xe,
                    Bar: () => Ve,
                    Default: () => je,
                    useVerticalScrollApi: () => Le
                });
                var r = t(7363),
                    i = t.n(r);
                const s = (e, u, t) => u.extraLargeHeight || u.largeHeight || u.mediumHeight || u.smallHeight || u.extraSmallHeight ? u.extraLargeHeight && t.extraLarge || u.largeHeight && t.large || u.mediumHeight && t.medium || u.smallHeight && t.small || u.extraSmallHeight && t.extraSmall ? e : null : e;
                var o = t(3138);
                const l = {
                    extraLarge: {
                        weight: 4,
                        width: 2560,
                        height: 1440
                    },
                    large: {
                        weight: 3,
                        width: 1920,
                        height: 1080
                    },
                    medium: {
                        weight: 2,
                        width: 1600,
                        height: 900
                    },
                    small: {
                        weight: 1,
                        width: 1366,
                        height: 768
                    },
                    extraSmall: {
                        weight: 0,
                        width: 1024,
                        height: 768
                    }
                };
                var c;

                function d(e, u, t) {
                    const a = function(e, u) {
                            switch (!0) {
                                case e >= u.extraLarge.width:
                                    return u.extraLarge.weight;
                                case e >= u.large.width && e < u.extraLarge.width:
                                    return u.large.weight;
                                case e >= u.medium.width && e < u.large.width:
                                    return u.medium.weight;
                                case e >= u.small.width && e < u.medium.width:
                                    return u.small.weight;
                                default:
                                    return u.extraSmall.weight
                            }
                        }(e, t),
                        n = function(e, u) {
                            switch (!0) {
                                case e >= u.extraLarge.height:
                                    return u.extraLarge.weight;
                                case e >= u.large.height && e < u.extraLarge.height:
                                    return u.large.weight;
                                case e >= u.medium.height && e < u.large.height:
                                    return u.medium.weight;
                                case e >= u.small.height && e < u.medium.height:
                                    return u.small.weight;
                                default:
                                    return u.extraSmall.weight
                            }
                        }(u, t),
                        r = Math.min(a, n);
                    return {
                        extraLarge: r === t.extraLarge.weight,
                        large: r === t.large.weight,
                        medium: r === t.medium.weight,
                        small: r === t.small.weight,
                        extraSmall: r === t.extraSmall.weight,
                        extraLargeWidth: a === t.extraLarge.weight,
                        largeWidth: a === t.large.weight,
                        mediumWidth: a === t.medium.weight,
                        smallWidth: a === t.small.weight,
                        extraSmallWidth: a === t.extraSmall.weight,
                        extraLargeHeight: n === t.extraLarge.weight,
                        largeHeight: n === t.large.weight,
                        mediumHeight: n === t.medium.weight,
                        smallHeight: n === t.small.weight,
                        extraSmallHeight: n === t.extraSmall.weight
                    }
                }! function(e) {
                    e.extraLarge = "extraLarge", e.large = "large", e.medium = "medium", e.small = "small", e.extraSmall = "extraSmall", e.extraLargeWidth = "extraLargeWidth", e.largeWidth = "largeWidth", e.mediumWidth = "mediumWidth", e.smallWidth = "smallWidth", e.extraSmallWidth = "extraSmallWidth", e.extraLargeHeight = "extraLargeHeight", e.largeHeight = "largeHeight", e.mediumHeight = "mediumHeight", e.smallHeight = "smallHeight", e.extraSmallHeight = "extraSmallHeight"
                }(c || (c = {}));
                const m = o.O.client.getSize("rem"),
                    _ = m.width,
                    E = m.height,
                    A = Object.assign({
                        width: _,
                        height: E
                    }, d(_, E, l)),
                    F = (0, r.createContext)(A),
                    g = ["children"];
                const D = e => {
                    let u = e.children,
                        t = function(e, u) {
                            if (null == e) return {};
                            var t, a, n = {},
                                r = Object.keys(e);
                            for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                            return n
                        }(e, g);
                    const a = (0, r.useContext)(F),
                        n = a.extraLarge,
                        i = a.large,
                        o = a.medium,
                        l = a.small,
                        c = a.extraSmall,
                        d = a.extraLargeWidth,
                        m = a.largeWidth,
                        _ = a.mediumWidth,
                        E = a.smallWidth,
                        A = a.extraSmallWidth,
                        D = a.extraLargeHeight,
                        C = a.largeHeight,
                        v = a.mediumHeight,
                        B = a.smallHeight,
                        p = a.extraSmallHeight,
                        f = {
                            extraLarge: D,
                            large: C,
                            medium: v,
                            small: B,
                            extraSmall: p
                        };
                    if (t.extraLarge || t.large || t.medium || t.small || t.extraSmall) {
                        if (t.extraLarge && n) return u;
                        if (t.large && i) return u;
                        if (t.medium && o) return u;
                        if (t.small && l) return u;
                        if (t.extraSmall && c) return u
                    } else {
                        if (t.extraLargeWidth && d) return s(u, t, f);
                        if (t.largeWidth && m) return s(u, t, f);
                        if (t.mediumWidth && _) return s(u, t, f);
                        if (t.smallWidth && E) return s(u, t, f);
                        if (t.extraSmallWidth && A) return s(u, t, f);
                        if (!(t.extraLargeWidth || t.largeWidth || t.mediumWidth || t.smallWidth || t.extraSmallWidth)) {
                            if (t.extraLargeHeight && D) return u;
                            if (t.largeHeight && C) return u;
                            if (t.mediumHeight && v) return u;
                            if (t.smallHeight && B) return u;
                            if (t.extraSmallHeight && p) return u
                        }
                    }
                    return null
                };
                D.defaultProps = {
                    extraLarge: !1,
                    large: !1,
                    medium: !1,
                    small: !1,
                    extraSmall: !1,
                    extraLargeWidth: !1,
                    largeWidth: !1,
                    mediumWidth: !1,
                    smallWidth: !1,
                    extraSmallWidth: !1,
                    extraLargeHeight: !1,
                    largeHeight: !1,
                    mediumHeight: !1,
                    smallHeight: !1,
                    extraSmallHeight: !1
                };
                (0, r.memo)(D);
                const C = e => {
                        const u = (0, r.useRef)(!1);
                        u.current || (e(), u.current = !0)
                    },
                    v = ({
                        children: e
                    }) => {
                        const u = (0, r.useContext)(F),
                            t = (0, r.useState)(u),
                            a = t[0],
                            n = t[1],
                            s = (0, r.useCallback)(((e, u) => {
                                const t = o.O.view.pxToRem(e),
                                    a = o.O.view.pxToRem(u);
                                n(Object.assign({
                                    width: t,
                                    height: a
                                }, d(t, a, l)))
                            }), []),
                            c = (0, r.useCallback)((() => {
                                const e = o.O.client.getSize("px");
                                s(e.width, e.height)
                            }), [s]);
                        C((() => {
                            o.O.client.events.on("clientResized", s), o.O.client.events.on("self.onScaleUpdated", c)
                        })), (0, r.useEffect)((() => () => {
                            o.O.client.events.off("clientResized", s), o.O.client.events.off("self.onScaleUpdated", c)
                        }), [s, c]);
                        const m = (0, r.useMemo)((() => Object.assign({}, a)), [a]);
                        return i().createElement(F.Provider, {
                            value: m
                        }, e)
                    };
                var B = t(6483),
                    p = t.n(B),
                    f = t(926),
                    b = t.n(f);
                let h, y, w;
                ! function(e) {
                    e[e.ExtraSmall = l.extraSmall.width] = "ExtraSmall", e[e.Small = l.small.width] = "Small", e[e.Medium = l.medium.width] = "Medium", e[e.Large = l.large.width] = "Large", e[e.ExtraLarge = l.extraLarge.width] = "ExtraLarge"
                }(h || (h = {})),
                function(e) {
                    e[e.ExtraSmall = l.extraSmall.width] = "ExtraSmall", e[e.Small = l.small.width] = "Small", e[e.Medium = l.medium.width] = "Medium", e[e.Large = l.large.width] = "Large", e[e.ExtraLarge = l.extraLarge.width] = "ExtraLarge"
                }(y || (y = {})),
                function(e) {
                    e[e.ExtraSmall = l.extraSmall.height] = "ExtraSmall", e[e.Small = l.small.height] = "Small", e[e.Medium = l.medium.height] = "Medium", e[e.Large = l.large.height] = "Large", e[e.ExtraLarge = l.extraLarge.height] = "ExtraLarge"
                }(w || (w = {}));
                const x = () => {
                        const e = (0, r.useContext)(F),
                            u = e.width,
                            t = e.height,
                            a = (e => {
                                switch (!0) {
                                    case e.extraLarge:
                                        return h.ExtraLarge;
                                    case e.large:
                                        return h.Large;
                                    case e.medium:
                                        return h.Medium;
                                    case e.small:
                                        return h.Small;
                                    case e.extraSmall:
                                        return h.ExtraSmall;
                                    default:
                                        return console.error("Unreachable media context resolution"), h.ExtraSmall
                                }
                            })(e),
                            n = (e => {
                                switch (!0) {
                                    case e.extraLargeWidth:
                                        return y.ExtraLarge;
                                    case e.largeWidth:
                                        return y.Large;
                                    case e.mediumWidth:
                                        return y.Medium;
                                    case e.smallWidth:
                                        return y.Small;
                                    case e.extraSmallWidth:
                                        return y.ExtraSmall;
                                    default:
                                        return console.error("Unreachable media context resolution"), y.ExtraSmall
                                }
                            })(e),
                            i = (e => {
                                switch (!0) {
                                    case e.extraLargeHeight:
                                        return w.ExtraLarge;
                                    case e.largeHeight:
                                        return w.Large;
                                    case e.mediumHeight:
                                        return w.Medium;
                                    case e.smallHeight:
                                        return w.Small;
                                    case e.extraSmallHeight:
                                        return w.ExtraSmall;
                                    default:
                                        return console.error("Unreachable media context resolution"), w.ExtraSmall
                                }
                            })(e);
                        return {
                            mediaSize: a,
                            mediaWidth: n,
                            mediaHeight: i,
                            remScreenWidth: u,
                            remScreenHeight: t
                        }
                    },
                    S = ["children", "className"];

                function L() {
                    return L = Object.assign || function(e) {
                        for (var u = 1; u < arguments.length; u++) {
                            var t = arguments[u];
                            for (var a in t) Object.prototype.hasOwnProperty.call(t, a) && (e[a] = t[a])
                        }
                        return e
                    }, L.apply(this, arguments)
                }
                const P = {
                        [y.ExtraSmall]: "",
                        [y.Small]: b().SMALL_WIDTH,
                        [y.Medium]: `${b().SMALL_WIDTH} ${b().MEDIUM_WIDTH}`,
                        [y.Large]: `${b().SMALL_WIDTH} ${b().MEDIUM_WIDTH} ${b().LARGE_WIDTH}`,
                        [y.ExtraLarge]: `${b().SMALL_WIDTH} ${b().MEDIUM_WIDTH} ${b().LARGE_WIDTH} ${b().EXTRA_LARGE_WIDTH}`
                    },
                    T = {
                        [w.ExtraSmall]: "",
                        [w.Small]: b().SMALL_HEIGHT,
                        [w.Medium]: `${b().SMALL_HEIGHT} ${b().MEDIUM_HEIGHT}`,
                        [w.Large]: `${b().SMALL_HEIGHT} ${b().MEDIUM_HEIGHT} ${b().LARGE_HEIGHT}`,
                        [w.ExtraLarge]: `${b().SMALL_HEIGHT} ${b().MEDIUM_HEIGHT} ${b().LARGE_HEIGHT} ${b().EXTRA_LARGE_HEIGHT}`
                    },
                    N = {
                        [h.ExtraSmall]: "",
                        [h.Small]: b().SMALL,
                        [h.Medium]: `${b().SMALL} ${b().MEDIUM}`,
                        [h.Large]: `${b().SMALL} ${b().MEDIUM} ${b().LARGE}`,
                        [h.ExtraLarge]: `${b().SMALL} ${b().MEDIUM} ${b().LARGE} ${b().EXTRA_LARGE}`
                    },
                    $ = e => {
                        let u = e.children,
                            t = e.className,
                            a = function(e, u) {
                                if (null == e) return {};
                                var t, a, n = {},
                                    r = Object.keys(e);
                                for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                                return n
                            }(e, S);
                        const n = x(),
                            r = n.mediaWidth,
                            s = n.mediaHeight,
                            o = n.mediaSize;
                        return i().createElement("div", L({
                            className: p()(t, P[r], T[s], N[o])
                        }, a), u)
                    },
                    k = ["children"];
                const M = e => {
                    let u = e.children,
                        t = function(e, u) {
                            if (null == e) return {};
                            var t, a, n = {},
                                r = Object.keys(e);
                            for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                            return n
                        }(e, k);
                    return i().createElement(v, null, i().createElement($, t, u))
                };
                var I = t(1533),
                    O = t.n(I);
                let H;
                ! function(e) {
                    e.Stats = "Stats", e.Reserves = "Reserves"
                }(H || (H = {}));
                var W = t(3403);

                function z() {}

                function U(e) {
                    return e
                }

                function V() {
                    return !1
                }
                console.log;
                var G = t(9174);

                function j(e, u) {
                    var t = "undefined" != typeof Symbol && e[Symbol.iterator] || e["@@iterator"];
                    if (t) return (t = t.call(e)).next.bind(t);
                    if (Array.isArray(e) || (t = function(e, u) {
                            if (!e) return;
                            if ("string" == typeof e) return X(e, u);
                            var t = Object.prototype.toString.call(e).slice(8, -1);
                            "Object" === t && e.constructor && (t = e.constructor.name);
                            if ("Map" === t || "Set" === t) return Array.from(e);
                            if ("Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t)) return X(e, u)
                        }(e)) || u && e && "number" == typeof e.length) {
                        t && (e = t);
                        var a = 0;
                        return function() {
                            return a >= e.length ? {
                                done: !0
                            } : {
                                done: !1,
                                value: e[a++]
                            }
                        }
                    }
                    throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                }

                function X(e, u) {
                    (null == u || u > e.length) && (u = e.length);
                    for (var t = 0, a = new Array(u); t < u; t++) a[t] = e[t];
                    return a
                }
                const q = e => 0 === e ? window : window.subViews.get(e);

                function K(e, u) {
                    return Array.isArray(e) ? e.map(u) : e.map(((e, t, a) => u(null == e ? void 0 : e.value, t, a)))
                }
                var Y = t(3946);
                const Z = ((e, u) => {
                        const t = (0, r.createContext)({});
                        return [function({
                            mode: a = "real",
                            options: n,
                            children: s,
                            mocks: l
                        }) {
                            const c = (0, r.useRef)([]),
                                d = (t, a, n) => {
                                    var r;
                                    const i = function({
                                            initializer: e = !0,
                                            rootId: u = 0,
                                            getRoot: t = q,
                                            context: a = "model"
                                        } = {}) {
                                            const n = new Map;

                                            function r(e, u = 0) {
                                                viewEnv.removeDataChangedCallback(e, u) ? n.delete(e) : console.error("Can't remove callback by id:", e)
                                            }
                                            engine.whenReady.then((() => {
                                                engine.on("viewEnv.onDataChanged", ((e, u, t) => {
                                                    t.forEach((u => {
                                                        const t = n.get(u);
                                                        void 0 !== t && t(e)
                                                    }))
                                                }))
                                            }));
                                            const i = e => {
                                                const n = t(u),
                                                    r = a.split(".").reduce(((e, u) => e[u]), n);
                                                return "string" != typeof e || 0 === e.length ? r : e.split(".").reduce(((e, u) => {
                                                    const t = e[u];
                                                    return "function" == typeof t ? t.bind(e) : t
                                                }), r)
                                            };
                                            return {
                                                subscribe: (t, r) => {
                                                    const s = "string" == typeof r ? `${a}.${r}` : a,
                                                        l = o.O.view.addModelObserver(s, u, !0);
                                                    return n.set(l, t), e && t(i(r)), l
                                                },
                                                readByPath: i,
                                                createCallback: (e, u) => {
                                                    const t = i(u);
                                                    return (...u) => {
                                                        t(e(...u))
                                                    }
                                                },
                                                createCallbackNoArgs: e => {
                                                    const u = i(e);
                                                    return () => {
                                                        u()
                                                    }
                                                },
                                                dispose: function() {
                                                    for (var e, t = j(n.keys()); !(e = t()).done;) r(e.value, u)
                                                },
                                                unsubscribe: r
                                            }
                                        }(a),
                                        s = "real" === t ? i : Object.assign({}, i, {
                                            readByPath: null != (r = null == n ? void 0 : n.getter) ? r : () => {}
                                        }),
                                        l = e => "mocks" === t ? null == n ? void 0 : n.getter(e) : s.readByPath(e),
                                        d = e => c.current.push(e),
                                        m = e({
                                            mode: t,
                                            readByPath: l,
                                            externalModel: s,
                                            observableModel: {
                                                array: (e, u) => {
                                                    const a = null != u ? u : l(e),
                                                        n = G.LO.box(a, {
                                                            equals: V
                                                        });
                                                    return "real" === t && s.subscribe((0, G.aD)((e => n.set(e))), e), n
                                                },
                                                object: (e, u) => {
                                                    const a = null != u ? u : l(e),
                                                        n = G.LO.box(a, {
                                                            equals: V
                                                        });
                                                    return "real" === t && s.subscribe((0, G.aD)((e => n.set(e))), e), n
                                                },
                                                primitives: (e, u) => {
                                                    const a = l(u);
                                                    if (Array.isArray(e)) {
                                                        const n = e.reduce(((e, u) => (e[u] = G.LO.box(a[u], {}), e)), {});
                                                        return "real" === t && s.subscribe((0, G.aD)((u => {
                                                            e.forEach((e => {
                                                                n[e].set(u[e])
                                                            }))
                                                        })), u), n
                                                    } {
                                                        const n = e,
                                                            r = Object.entries(n),
                                                            i = r.reduce(((e, [u, t]) => (e[t] = G.LO.box(a[u], {}), e)), {});
                                                        return "real" === t && s.subscribe((0, G.aD)((e => {
                                                            r.forEach((([u, t]) => {
                                                                i[t].set(e[u])
                                                            }))
                                                        })), u), i
                                                    }
                                                }
                                            },
                                            cleanup: d
                                        }),
                                        _ = {
                                            mode: t,
                                            model: m,
                                            externalModel: s,
                                            cleanup: d
                                        };
                                    return {
                                        model: m,
                                        controls: "mocks" === t && n ? n.controls(_) : u(_),
                                        externalModel: s,
                                        mode: t
                                    }
                                },
                                m = (0, r.useRef)(!1),
                                _ = (0, r.useState)(a),
                                E = _[0],
                                A = _[1],
                                F = (0, r.useState)((() => d(a, n, l))),
                                g = F[0],
                                D = F[1];
                            return (0, r.useEffect)((() => {
                                m.current ? D(d(E, n, l)) : m.current = !0
                            }), [l, E, n]), (0, r.useEffect)((() => {
                                A(a)
                            }), [a]), (0, r.useEffect)((() => () => {
                                g.externalModel.dispose(), c.current.forEach((e => e()))
                            }), [g]), i().createElement(t.Provider, {
                                value: g
                            }, s)
                        }, () => (0, r.useContext)(t)]
                    })((({
                        observableModel: e
                    }) => {
                        const u = Object.assign({
                                reserveGroups: e.array("personalReserves.reserveGroups", [])
                            }, e.primitives(["tabSelection"])),
                            t = (0, Y.Om)((() => K(u.reserveGroups.get(), (({
                                category: e
                            }) => e)))),
                            a = (0, Y.Om)((() => K(u.reserveGroups.get(), U))),
                            n = (0, Y.Om)((e => {
                                const u = a().find((u => u.category === e));
                                if (!u) return [];
                                return K(u.reserves, (e => {
                                    const u = K(e.price.prices, (e => {
                                            const u = K(e.price, (e => ({
                                                    value: Object.assign({}, e)
                                                }))),
                                                t = K(e.defPrice, (e => ({
                                                    value: Object.assign({}, e)
                                                }))),
                                                a = K(e.discount, (e => ({
                                                    value: Object.assign({}, e)
                                                })));
                                            return {
                                                value: Object.assign({}, e, {
                                                    price: u,
                                                    defPrice: t,
                                                    discount: a
                                                })
                                            }
                                        })),
                                        t = {
                                            prices: u
                                        };
                                    return Object.assign({}, e, {
                                        price: t
                                    })
                                }))
                            }));
                        return Object.assign({}, u, {
                            computes: {
                                getReserveCategoryNames: t,
                                getReserveCategoryItems: n
                            }
                        })
                    }), (({
                        externalModel: e
                    }) => ({
                        onBoosterActivate: e.createCallback((e => e), "personalReserves.onBoosterActivate")
                    }))),
                    Q = Z[0],
                    J = Z[1],
                    ee = e => {
                        let u, t = null;
                        return t = requestAnimationFrame((() => {
                            t = requestAnimationFrame((() => {
                                t = null, u = e()
                            }))
                        })), () => {
                            "function" == typeof u && u(), null !== t && cancelAnimationFrame(t)
                        }
                    },
                    ue = (e, u, t) => t < e ? e : t > u ? u : t,
                    te = [];

                function ae(e) {
                    const u = (0, r.useRef)(e);
                    return (0, r.useLayoutEffect)((() => {
                        u.current = e
                    })), (0, r.useCallback)(((...e) => (0, u.current)(...e)), te)
                }

                function ne(e, u, t = []) {
                    const a = (0, r.useRef)(0),
                        n = (0, r.useCallback)((() => window.clearInterval(a.current)), t || []);
                    (0, r.useEffect)((() => n), [n]);
                    const i = (null != t ? t : []).concat([u]);
                    return [(0, r.useCallback)((t => {
                        a.current = window.setInterval((() => e(t, !0)), u), e(t, !1)
                    }), i), n]
                }

                function re(e) {
                    engine.call("PlaySound", e).catch((u => {
                        console.error("[lib/sounds.js] playSound(", e, "): ", u)
                    }))
                }

                function ie(e, u) {
                    var t = "undefined" != typeof Symbol && e[Symbol.iterator] || e["@@iterator"];
                    if (t) return (t = t.call(e)).next.bind(t);
                    if (Array.isArray(e) || (t = function(e, u) {
                            if (!e) return;
                            if ("string" == typeof e) return se(e, u);
                            var t = Object.prototype.toString.call(e).slice(8, -1);
                            "Object" === t && e.constructor && (t = e.constructor.name);
                            if ("Map" === t || "Set" === t) return Array.from(e);
                            if ("Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t)) return se(e, u)
                        }(e)) || u && e && "number" == typeof e.length) {
                        t && (e = t);
                        var a = 0;
                        return function() {
                            return a >= e.length ? {
                                done: !0
                            } : {
                                done: !1,
                                value: e[a++]
                            }
                        }
                    }
                    throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                }

                function se(e, u) {
                    (null == u || u > e.length) && (u = e.length);
                    for (var t = 0, a = new Array(u); t < u; t++) a[t] = e[t];
                    return a
                }

                function oe(e, u, t) {
                    const a = (0, r.useMemo)((() => function(e, u, t, a) {
                        let n, r = !1,
                            i = 0;

                        function s() {
                            n && clearTimeout(n)
                        }

                        function o(...o) {
                            const l = this,
                                c = Date.now() - i;

                            function d() {
                                i = Date.now(), t.apply(l, o)
                            }
                            r || (a && !n && d(), s(), void 0 === a && c > e ? d() : !0 !== u && (n = setTimeout(a ? function() {
                                n = void 0
                            } : d, void 0 === a ? e - c : e)))
                        }
                        return "boolean" != typeof u && (a = t, t = u, u = void 0), o.cancel = function() {
                            s(), r = !0
                        }, o
                    }(t, e)), u);
                    return (0, r.useEffect)((() => a.cancel), [a]), a
                }
                var le = t(7030);
                let ce;
                ! function(e) {
                    e[e.Next = -1] = "Next", e[e.Prev = 1] = "Prev"
                }(ce || (ce = {}));
                const de = {
                        step: {
                            type: "proportional",
                            factor: 4,
                            clampedArrowStepTimeout: 100
                        },
                        animationConfig: {
                            tension: 170,
                            friction: 26
                        }
                    },
                    me = ({
                        getContainerSize: e,
                        getBounds: u,
                        setScrollPosition: t,
                        getDirection: a,
                        getWrapperSize: n,
                        forceTriggerMouseMove: i
                    }) => {
                        const s = (e, t) => {
                            const a = u(e),
                                n = a[0],
                                r = a[1];
                            return r <= n ? 0 : ue(n, r, t)
                        };
                        return (o = {}) => {
                            const l = o.settings,
                                c = void 0 === l ? de : l,
                                d = (0, r.useRef)(null),
                                m = (0, r.useRef)(null),
                                _ = (0, r.useRef)(!1),
                                E = (() => {
                                    const e = (0, r.useMemo)((() => ({})), []),
                                        u = u => (e[u] || (e[u] = new Map), e[u]),
                                        t = (e, t) => {
                                            u(e).set(t, t)
                                        },
                                        a = (e, t) => {
                                            u(e).delete(t)
                                        },
                                        n = (e, ...t) => {
                                            for (var a, n = ie(u(e).values()); !(a = n()).done;)(0, a.value)(...t)
                                        };
                                    return (0, r.useMemo)((() => ({
                                        on: t,
                                        off: a,
                                        trigger: n
                                    })), [])
                                })(),
                                A = oe((() => {
                                    i && i()
                                }), [], 150),
                                F = (0, le.useSpring)((() => ({
                                    scrollPosition: 0,
                                    onChange: e => {
                                        const u = d.current;
                                        u && (t(u, e), E.trigger("change", e), i && _.current && A())
                                    },
                                    onRest: e => E.trigger("rest", e),
                                    onStart: e => E.trigger("start", e),
                                    onPause: e => E.trigger("pause", e)
                                }))),
                                g = F[0],
                                D = F[1],
                                C = (0, r.useCallback)(((e, u, t) => {
                                    var a;
                                    const n = g.scrollPosition.get(),
                                        r = (null != (a = g.scrollPosition.goal) ? a : 0) - n;
                                    return s(e, u * t + r + n)
                                }), [g.scrollPosition]),
                                v = (0, r.useCallback)(((e, {
                                    immediate: u = !1,
                                    reset: t = !0
                                } = {}) => {
                                    const a = d.current;
                                    a && D.start({
                                        scrollPosition: s(a, e),
                                        immediate: u,
                                        reset: t,
                                        config: c.animationConfig,
                                        from: {
                                            scrollPosition: s(a, g.scrollPosition.get())
                                        }
                                    })
                                }), [D, c.animationConfig, g.scrollPosition]),
                                B = (0, r.useCallback)((e => {
                                    const u = d.current,
                                        t = m.current;
                                    if (!u || !t) return;
                                    const a = ((e, u) => {
                                            switch (u.type) {
                                                case "proportional":
                                                    return n(e) / u.factor;
                                                case "fixed":
                                                    return u.value
                                            }
                                        })(t, c.step),
                                        r = C(u, e, a);
                                    v(r)
                                }), [v, C, c.step]),
                                p = (0, r.useCallback)((e => {
                                    0 !== e.deltaY && B(a(e)), d.current && E.trigger("mouseWheel", e, g.scrollPosition, u(d.current))
                                }), [g.scrollPosition, B, E]),
                                f = ((e, u = []) => {
                                    const t = (0, r.useRef)(),
                                        a = (0, r.useCallback)(((...u) => {
                                            t.current && t.current(), t.current = e(...u)
                                        }), u);
                                    return (0, r.useEffect)((() => () => {
                                        t.current && t.current()
                                    }), [a]), a
                                })((() => ee((() => {
                                    const e = d.current;
                                    e && (v(s(e, g.scrollPosition.goal), {
                                        immediate: !0
                                    }), E.trigger("resizeHandled"))
                                }))), [v, g.scrollPosition.goal]),
                                b = ae((() => {
                                    const e = d.current;
                                    if (!e) return;
                                    const u = s(e, g.scrollPosition.goal);
                                    u !== g.scrollPosition.goal && v(u, {
                                        immediate: !0
                                    }), E.trigger("recalculateContent")
                                }));
                            (0, r.useEffect)((() => (window.addEventListener("resize", f), () => {
                                window.removeEventListener("resize", f)
                            })), [f]), (0, r.useEffect)((() => {
                                const e = d.current;
                                if (!e || !i) return;
                                const u = () => {
                                        _.current = !0
                                    },
                                    t = () => {
                                        _.current = !1
                                    };
                                return e.addEventListener("mouseenter", u), e.addEventListener("mouseleave", t), () => {
                                    e.removeEventListener("mouseenter", u), e.removeEventListener("mouseleave", t)
                                }
                            }), [d]);
                            return (0, r.useMemo)((() => ({
                                getWrapperSize: () => m.current ? n(m.current) : void 0,
                                getContainerSize: () => d.current ? e(d.current) : void 0,
                                getBounds: () => d.current ? u(d.current) : (console.warn("getBounds: contentRef.current is null"), [0, 0]),
                                stepTimeout: c.step.clampedArrowStepTimeout,
                                clampPosition: s,
                                handleMouseWheel: p,
                                applyScroll: v,
                                applyStepTo: B,
                                contentRef: d,
                                wrapperRef: m,
                                scrollPosition: D,
                                animationScroll: g,
                                recalculateContent: b,
                                events: {
                                    on: E.on,
                                    off: E.off
                                }
                            })), [g.scrollPosition, v, B, E.off, E.on, b, p, D, c.step.clampedArrowStepTimeout])
                        }
                    },
                    _e = me({
                        getBounds: e => {
                            var u, t;
                            return [0, e.offsetWidth - (null != (u = null == (t = e.parentElement) ? void 0 : t.offsetWidth) ? u : 0)]
                        },
                        getContainerSize: e => e.offsetWidth,
                        getWrapperSize: e => e.offsetWidth,
                        setScrollPosition: (e, u) => {
                            e.style.transform = `translateX(-${u.value.scrollPosition}px)`
                        },
                        getDirection: e => e.deltaY > 1 ? ce.Next : ce.Prev,
                        forceTriggerMouseMove: o.O.view.forceTriggerMouseMove
                    }),
                    Ee = "HorizontalBar_base_49",
                    Ae = "HorizontalBar_base__nonActive_82",
                    Fe = "HorizontalBar_leftButton_5f",
                    ge = "HorizontalBar_rightButton_03",
                    De = "HorizontalBar_track_0d",
                    Ce = "HorizontalBar_thumb_fd",
                    ve = "HorizontalBar_rail_32",
                    Be = "disable",
                    pe = {
                        pending: !1,
                        offset: 0
                    },
                    fe = e => {
                        var u;
                        return .9 * (null != (u = e.getWrapperSize()) ? u : 0)
                    },
                    be = () => {},
                    he = (e, u) => Math.max(20, e.offsetWidth * u),
                    ye = (0, r.memo)((({
                        api: e,
                        classNames: u = {},
                        getStepByRailClick: t = fe,
                        onDrag: a = be
                    }) => {
                        const n = (0, r.useRef)(null),
                            s = (0, r.useRef)(null),
                            l = (0, r.useRef)(null),
                            c = (0, r.useRef)(null),
                            d = (0, r.useRef)(null),
                            m = e.stepTimeout || 100,
                            _ = (0, r.useState)(pe),
                            E = _[0],
                            A = _[1],
                            F = (0, r.useCallback)((e => {
                                A(e), d.current && a({
                                    type: e.pending ? "dragStart" : "dragEnd",
                                    thumb: d.current
                                })
                            }), [a]),
                            g = () => {
                                const u = c.current,
                                    t = d.current,
                                    a = e.getWrapperSize(),
                                    n = e.getContainerSize();
                                if (!(a && u && t && n)) return;
                                const r = e.animationScroll.scrollPosition.get(),
                                    i = Math.min(1, a / n),
                                    o = ue(0, 1, r / (n - a)),
                                    m = (u.offsetWidth - he(u, i)) * o;
                                t.style.transform = `translateX(${0|m}px)`, (e => {
                                    if (s.current && l.current && c.current && d.current) {
                                        if (0 === e) return s.current.classList.add(Be), void l.current.classList.remove(Be);
                                        if (u = c.current, t = d.current, e - (u.offsetWidth - t.offsetWidth) >= -.5) return s.current.classList.remove(Be), void l.current.classList.add(Be);
                                        var u, t;
                                        s.current.classList.remove(Be), l.current.classList.remove(Be)
                                    }
                                })(m)
                            },
                            D = ae((() => {
                                (() => {
                                    const u = d.current,
                                        t = c.current,
                                        a = e.getWrapperSize(),
                                        r = e.getContainerSize();
                                    if (!(r && u && a && t)) return;
                                    const i = Math.min(1, a / r);
                                    u.style.width = `${he(t,i)}px`, u.style.display = "flex", n.current && (1 === i ? n.current.classList.add(Ae) : n.current.classList.remove(Ae))
                                })(), g()
                            }));
                        (0, r.useEffect)((() => ee(D))), (0, r.useEffect)((() => ee((() => {
                            const u = () => {
                                g()
                            };
                            let t = be;
                            const a = () => {
                                t(), t = ee(D)
                            };
                            return e.events.on("recalculateContent", D), e.events.on("rest", u), e.events.on("change", u), e.events.on("resizeHandled", a), () => {
                                t(), e.events.off("recalculateContent", D), e.events.off("rest", u), e.events.off("change", u), e.events.off("resizeHandled", a)
                            }
                        }))), [e]), (0, r.useEffect)((() => {
                            if (!E.pending) return;
                            const u = o.O.client.events.mouse.move((([u, t]) => {
                                    var n;
                                    const r = e.contentRef.current,
                                        i = e.wrapperRef.current;
                                    if (!r || !i) return;
                                    const s = c.current,
                                        o = d.current;
                                    if (!s || !o) return;
                                    if ("inside" === t && u.clientX < 0) return;
                                    const l = u.clientX - E.offset - s.getBoundingClientRect().x,
                                        m = l / s.offsetWidth * (null != (n = e.getContainerSize()) ? n : 0);
                                    e.scrollPosition.start({
                                        scrollPosition: e.clampPosition(r, m),
                                        reset: !0,
                                        immediate: !0,
                                        from: {
                                            scrollPosition: e.animationScroll.scrollPosition.get()
                                        }
                                    }), a({
                                        type: "dragging",
                                        thumb: o,
                                        thumbOffset: l,
                                        contentOffset: m
                                    })
                                })),
                                t = o.O.client.events.mouse.up((() => {
                                    u(), F(pe)
                                }));
                            return () => {
                                u(), t()
                            }
                        }), [e, E.offset, E.pending, a, F]);
                        const C = ne((u => e.applyStepTo(u)), m, [e]),
                            v = C[0],
                            B = C[1];
                        (0, r.useEffect)((() => (document.addEventListener("mouseup", B, !0), () => document.removeEventListener("mouseup", B, !0))), [B]);
                        const f = e => {
                            e.target.classList.contains(Be) || re("highlight")
                        };
                        return i().createElement("div", {
                            className: p()(Ee, u.base),
                            ref: n,
                            onWheel: e.handleMouseWheel
                        }, i().createElement("div", {
                            className: p()(Fe, u.leftButton),
                            onMouseDown: e => {
                                e.target.classList.contains(Be) || 0 !== e.button || (re("play"), v(ce.Next))
                            },
                            onMouseUp: B,
                            ref: s,
                            onMouseEnter: f
                        }), i().createElement("div", {
                            className: p()(De, u.track),
                            onMouseDown: u => {
                                const a = d.current;
                                if (a && 0 === u.button)
                                    if (re("play"), u.target === a) F({
                                        pending: !0,
                                        offset: u.screenX - a.getBoundingClientRect().x
                                    });
                                    else {
                                        (u => {
                                            const a = d.current,
                                                n = e.contentRef.current;
                                            if (!a || !n) return;
                                            const r = t(e);
                                            e.applyScroll(e.animationScroll.scrollPosition.get() + r * u)
                                        })(u.screenX > a.getBoundingClientRect().x ? ce.Prev : ce.Next)
                                    }
                            },
                            ref: c,
                            onMouseEnter: f
                        }, i().createElement("div", {
                            ref: d,
                            className: p()(Ce, u.thumb)
                        }), i().createElement("div", {
                            className: p()(ve, u.rail)
                        })), i().createElement("div", {
                            className: p()(ge, u.rightButton),
                            onMouseDown: e => {
                                e.target.classList.contains(Be) || 0 !== e.button || (re("play"), v(ce.Prev))
                            },
                            onMouseUp: B,
                            ref: l,
                            onMouseEnter: f
                        }))
                    })),
                    we = {
                        base: "HorizontalScroll_base_29",
                        wrapper: "HorizontalScroll_wrapper_1e",
                        defaultScrollArea: "HorizontalScroll_defaultScrollArea_8d"
                    },
                    xe = ({
                        children: e,
                        api: u,
                        className: t,
                        barClassNames: a,
                        areaClassName: n,
                        classNames: s,
                        scrollClassName: o,
                        getStepByRailClick: l,
                        onDrag: c
                    }) => {
                        const d = (0, r.useMemo)((() => {
                                const e = a || {};
                                return Object.assign({}, e, {
                                    base: p()(we.base, e.base)
                                })
                            }), [a]),
                            m = (0, r.useMemo)((() => Object.assign({}, u, {
                                handleMouseWheel: () => {}
                            })), [u]);
                        return i().createElement("div", {
                            className: p()(we.defaultScroll, t),
                            onWheel: u.handleMouseWheel
                        }, i().createElement("div", {
                            className: p()(we.defaultScrollArea, n)
                        }, i().createElement(Se, {
                            className: o,
                            api: m,
                            classNames: s
                        }, e)), i().createElement(ye, {
                            getStepByRailClick: l,
                            api: u,
                            onDrag: c,
                            classNames: d
                        }))
                    },
                    Se = ({
                        api: e,
                        className: u,
                        classNames: t,
                        children: a
                    }) => ((0, r.useEffect)((() => ee(e.recalculateContent))), i().createElement("div", {
                        className: p()(we.base, u)
                    }, i().createElement("div", {
                        className: p()(we.wrapper, null == t ? void 0 : t.wrapper),
                        onWheel: e.handleMouseWheel,
                        ref: e.wrapperRef
                    }, i().createElement("div", {
                        className: p()(we.content, null == t ? void 0 : t.content),
                        ref: e.contentRef
                    }, a))));
                Se.Bar = ye, Se.Default = xe;
                const Le = me({
                        getBounds: e => [0, e.scrollHeight - e.offsetHeight],
                        getContainerSize: e => e.scrollHeight,
                        getWrapperSize: e => e.offsetHeight,
                        setScrollPosition: (e, u) => {
                            e.scrollTop = u.value.scrollPosition
                        },
                        getDirection: e => e.deltaY > 1 ? ce.Next : ce.Prev
                    }),
                    Pe = "VerticalBar_base_f3",
                    Re = "VerticalBar_base__nonActive_42",
                    Te = "VerticalBar_topButton_d7",
                    Ne = "VerticalBar_bottomButton_06",
                    $e = "VerticalBar_track_df",
                    ke = "VerticalBar_thumb_32",
                    Me = "VerticalBar_rail_43",
                    Ie = "disable",
                    Oe = () => {},
                    He = {
                        pending: !1,
                        offset: 0
                    },
                    We = e => {
                        var u;
                        return .9 * (null != (u = e.getWrapperSize()) ? u : 0)
                    },
                    ze = (e, u) => {
                        e.contentRef.current && u(e.contentRef.current)
                    },
                    Ue = (e, u) => Math.max(20, e.offsetHeight * u),
                    Ve = (0, r.memo)((({
                        api: e,
                        classNames: u = {},
                        getStepByRailClick: t = We,
                        onDrag: a = Oe
                    }) => {
                        const n = (0, r.useRef)(null),
                            s = (0, r.useRef)(null),
                            l = (0, r.useRef)(null),
                            c = (0, r.useRef)(null),
                            d = (0, r.useRef)(null),
                            m = e.stepTimeout || 100,
                            _ = (0, r.useState)(He),
                            E = _[0],
                            A = _[1],
                            F = (0, r.useCallback)((e => {
                                A(e), d.current && a({
                                    type: e.pending ? "dragStart" : "dragEnd",
                                    thumb: d.current
                                })
                            }), [a]),
                            g = ae((() => {
                                const u = d.current,
                                    t = c.current,
                                    a = e.getWrapperSize(),
                                    r = e.getContainerSize();
                                if (!(a && r && u && t)) return;
                                const i = Math.min(1, a / r);
                                return u.style.height = `${Ue(t,i)}px`, u.style.display = "flex", n.current && (1 === i ? n.current.classList.add(Re) : n.current.classList.remove(Re)), i
                            })),
                            D = ae((() => {
                                const u = c.current,
                                    t = d.current,
                                    a = e.getWrapperSize(),
                                    n = e.getContainerSize();
                                if (!(a && u && t && n)) return;
                                const r = e.animationScroll.scrollPosition.get(),
                                    i = Math.min(1, a / n),
                                    o = ue(0, 1, r / (n - a)),
                                    m = (u.offsetHeight - Ue(u, i)) * o;
                                t.style.transform = `translateY(${0|m}px)`, (e => {
                                    if (s.current && l.current && c.current && d.current) {
                                        if (0 === Math.round(e)) return s.current.classList.add(Ie), void l.current.classList.remove(Ie);
                                        if (u = c.current, t = d.current, e - (u.offsetHeight - t.offsetHeight) >= -.5) return s.current.classList.remove(Ie), void l.current.classList.add(Ie);
                                        var u, t;
                                        s.current.classList.remove(Ie), l.current.classList.remove(Ie)
                                    }
                                })(m)
                            })),
                            C = ae((() => {
                                ze(e, (() => {
                                    g(), D()
                                }))
                            }));
                        (0, r.useEffect)((() => ee(C))), (0, r.useEffect)((() => {
                            const u = () => {
                                ze(e, (() => {
                                    D()
                                }))
                            };
                            let t = Oe;
                            const a = () => {
                                t(), t = ee(C)
                            };
                            return e.events.on("recalculateContent", C), e.events.on("rest", u), e.events.on("change", u), e.events.on("resizeHandled", a), () => {
                                t(), e.events.off("recalculateContent", C), e.events.off("rest", u), e.events.off("change", u), e.events.off("resizeHandled", a)
                            }
                        }), [e]), (0, r.useEffect)((() => {
                            if (!E.pending) return;
                            const u = o.O.client.events.mouse.up((() => {
                                    F(He)
                                })),
                                t = o.O.client.events.mouse.move((([u]) => {
                                    ze(e, (t => {
                                        const n = c.current,
                                            r = d.current,
                                            i = e.getContainerSize();
                                        if (!n || !r || !i) return;
                                        const s = u.screenY - E.offset - n.getBoundingClientRect().y,
                                            o = s / n.offsetHeight * i;
                                        e.scrollPosition.start({
                                            scrollPosition: e.clampPosition(t, o),
                                            reset: !0,
                                            immediate: !0,
                                            from: {
                                                scrollPosition: t.scrollTop
                                            }
                                        }), a({
                                            type: "dragging",
                                            thumb: r,
                                            thumbOffset: s,
                                            contentOffset: o
                                        })
                                    }))
                                }));
                            return () => {
                                u(), t()
                            }
                        }), [e, E.offset, E.pending, a, F]);
                        const v = ne((u => e.applyStepTo(u)), m, [e]),
                            B = v[0],
                            f = v[1];
                        (0, r.useEffect)((() => (document.addEventListener("mouseup", f, !0), () => document.removeEventListener("mouseup", f, !0))), [f]);
                        const b = e => {
                            e.target.classList.contains(Ie) || re("highlight")
                        };
                        return i().createElement("div", {
                            className: p()(Pe, u.base),
                            ref: n,
                            onWheel: e.handleMouseWheel
                        }, i().createElement("div", {
                            className: p()(Te, u.topButton),
                            onMouseDown: e => {
                                e.target.classList.contains(Ie) || 0 !== e.button || (re("play"), B(ce.Next))
                            },
                            ref: s,
                            onMouseEnter: b
                        }), i().createElement("div", {
                            className: p()($e, u.track),
                            onMouseDown: u => {
                                const a = d.current;
                                if (a && 0 === u.button)
                                    if (re("play"), u.target === a) F({
                                        pending: !0,
                                        offset: u.screenY - a.getBoundingClientRect().y
                                    });
                                    else {
                                        (u => {
                                            d.current && ze(e, (a => {
                                                if (!a) return;
                                                const n = t(e),
                                                    r = e.clampPosition(a, a.scrollTop + n * u);
                                                e.applyScroll(r)
                                            }))
                                        })(u.screenY > a.getBoundingClientRect().y ? ce.Prev : ce.Next)
                                    }
                            },
                            ref: c,
                            onMouseEnter: b
                        }, i().createElement("div", {
                            ref: d,
                            className: p()(ke, u.thumb)
                        }), i().createElement("div", {
                            className: p()(Me, u.rail)
                        })), i().createElement("div", {
                            className: p()(Ne, u.bottomButton),
                            onMouseDown: e => {
                                e.target.classList.contains(Ie) || 0 !== e.button || (re("play"), B(ce.Prev))
                            },
                            onMouseUp: f,
                            ref: l,
                            onMouseEnter: b
                        }))
                    })),
                    Ge = {
                        content: "VerticalScroll_content_cb",
                        defaultScroll: "VerticalScroll_defaultScroll_f8",
                        bar: "VerticalScroll_bar_1e",
                        area: "VerticalScroll_area_af"
                    },
                    je = ({
                        children: e,
                        api: u,
                        className: t,
                        barClassNames: a,
                        areaClassName: n,
                        scrollClassName: s,
                        scrollClassNames: o,
                        getStepByRailClick: l,
                        onDrag: c
                    }) => {
                        const d = (0, r.useMemo)((() => {
                                const e = a || {};
                                return Object.assign({}, e, {
                                    base: p()(Ge.base, e.base)
                                })
                            }), [a]),
                            m = (0, r.useMemo)((() => Object.assign({}, u, {
                                handleMouseWheel: () => {}
                            })), [u]);
                        return i().createElement("div", {
                            className: p()(Ge.defaultScroll, t),
                            onWheel: u.handleMouseWheel
                        }, i().createElement("div", {
                            className: p()(Ge.area, n)
                        }, i().createElement(Xe, {
                            className: s,
                            classNames: o,
                            api: m
                        }, e)), i().createElement(Ve, {
                            getStepByRailClick: l,
                            api: u,
                            onDrag: c,
                            classNames: d
                        }))
                    },
                    Xe = ({
                        className: e,
                        classNames: u,
                        children: t,
                        api: a
                    }) => ((0, r.useEffect)((() => ee(a.recalculateContent))), i().createElement("div", {
                        className: p()(Ge.base, e),
                        ref: a.wrapperRef,
                        onWheel: a.handleMouseWheel
                    }, i().createElement("div", {
                        className: p()(Ge.content, null == u ? void 0 : u.content),
                        ref: a.contentRef
                    }, t)));
                Xe.Default = je;
                const qe = {
                    Vertical: n,
                    Horizontal: a
                };
                let Ke, Ye, Ze;
                ! function(e) {
                    e.Unavailable = "unavailable", e.CommendFirst = "commendFirst", e.CommendBack = "commendBack", e.OutgoingCommendation = "outgoingCommendation", e.MutualCommendation = "mutualCommendation"
                }(Ke || (Ke = {})),
                function(e) {
                    e.AtSpg = "atSpg", e.HeavyTank = "heavyTank", e.LightTank = "lightTank", e.MediumTank = "mediumTank", e.Spg = "spg", e.Undefined = "undefined"
                }(Ye || (Ye = {})),
                function(e) {
                    e.IRON = "iron", e.BRONZE = "bronze", e.SILVER = "silver", e.GOLD = "gold", e.ENAMEL = "enamel", e.MAXIMUM = "prestige", e.UNDEFINED = "undefined"
                }(Ze || (Ze = {}));
                const Qe = "PrimitiveTooltip_base_b8",
                    Je = "PrimitiveTooltip_body_97",
                    eu = "PrimitiveTooltip_body__short_b6",
                    uu = "PrimitiveTooltip_body__top_57",
                    tu = "PrimitiveTooltip_body__reflected_e8",
                    au = "PrimitiveTooltip_header_96",
                    nu = "PrimitiveTooltip_content_c1",
                    ru = ["className", "header", "content", "isShort", "reflected", "children", "contentWrapperProps"];

                function iu() {
                    return iu = Object.assign || function(e) {
                        for (var u = 1; u < arguments.length; u++) {
                            var t = arguments[u];
                            for (var a in t) Object.prototype.hasOwnProperty.call(t, a) && (e[a] = t[a])
                        }
                        return e
                    }, iu.apply(this, arguments)
                }

                function su(e) {
                    let u = e.className,
                        t = e.header,
                        a = e.content,
                        n = e.isShort,
                        r = void 0 !== n && n,
                        s = e.reflected,
                        o = void 0 !== s && s,
                        l = e.children,
                        c = e.contentWrapperProps,
                        d = function(e, u) {
                            if (null == e) return {};
                            var t, a, n = {},
                                r = Object.keys(e);
                            for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                            return n
                        }(e, ru);
                    return i().createElement("div", iu({
                        className: p()(Qe, u)
                    }, d), l, i().createElement("div", {
                        className: p()(Je, r && eu, o && tu),
                        "data-bind-class-toggle": `${uu}:({{index}} > 9 && {{index}} < 15) || {{index}} > 23;`
                    }, i().createElement("div", c), t && i().createElement("div", {
                        className: au
                    }, t), a && i().createElement("div", {
                        className: nu
                    }, a)))
                }
                const ou = {
                        commendation: "CommendationLike_commendation_e1",
                        tooltip_trigger: "CommendationLike_tooltip_trigger_28",
                        commendation__placeholder: "CommendationLike_commendation__placeholder_7d",
                        commendation__first: "CommendationLike_commendation__first_67",
                        like_animation: "CommendationLike_like_animation_10",
                        commendation__back: "CommendationLike_commendation__back_92",
                        tooltip_trigger__anim: "CommendationLike_tooltip_trigger__anim_8b",
                        commendation__unavailable: "CommendationLike_commendation__unavailable_2c",
                        commendation__mutual: "CommendationLike_commendation__mutual_95",
                        fist_left: "CommendationLike_fist_left_cf",
                        fist_left__anim: "CommendationLike_fist_left__anim_bb",
                        fist_bump_left: "CommendationLike_fist_bump_left_62",
                        fist_right: "CommendationLike_fist_right_20",
                        fist_right__anim: "CommendationLike_fist_right__anim_a2",
                        fist_bump_right: "CommendationLike_fist_bump_right_1e",
                        commendation__outgoing_commend: "CommendationLike_commendation__outgoing_commend_5a"
                    },
                    lu = ({
                        path: e
                    }) => i().createElement("div", {
                        "data-bind-if": "{{model.playerList.isCommendationEnabled}}"
                    }, i().createElement("div", {
                        className: p()(ou.commendation, ou.commendation__placeholder),
                        "data-bind-if": `{{${e}.isCurrentPlayer}}`
                    }), i().createElement(su, {
                        className: p()(ou.commendation, ou.commendation__first),
                        header: R.strings.tooltips.commendations.comms_likes_sct_txt_h_02(),
                        content: R.strings.tooltips.commendations.comms_likes_sct_txt_t_02(),
                        "data-bind-if": `{{${e}.commendationStateModel.commendationState}} === '${Ke.CommendFirst}' && !{{${e}.isCurrentPlayer}}`,
                        "data-bind-click": `model.playerList.onPlayerCommend({ vehicleId: {{${e}.vehicleId}} })`
                    }, i().createElement("div", {
                        className: ou.tooltip_trigger
                    })), i().createElement(su, {
                        "data-bind-class-toggle": `${ou.commendation__back__anim}:{{${e}.commendationStateModel.isNewState}} && {{model.showCommendationAnimations}}`,
                        className: p()(ou.commendation, ou.commendation__back),
                        header: R.strings.tooltips.commendations.comms_likes_sct_txt_h_03(),
                        content: R.strings.tooltips.commendations.comms_likes_sct_txt_t_03(),
                        "data-bind-if": `{{${e}.commendationStateModel.commendationState}} === '${Ke.CommendBack}' && !{{${e}.isCurrentPlayer}}`,
                        "data-bind-click": `model.playerList.onPlayerCommend({ vehicleId: {{${e}.vehicleId}} })`
                    }, i().createElement("div", {
                        className: ou.tooltip_trigger
                    })), i().createElement(su, {
                        className: p()(ou.commendation, ou.commendation__unavailable),
                        header: R.strings.tooltips.commendations.comms_likes_sct_txt_h_01(),
                        content: R.strings.tooltips.commendations.comms_likes_sct_txt_t_01(),
                        "data-bind-if": `{{${e}.commendationStateModel.commendationState}} === '${Ke.Unavailable}' && !{{${e}.isCurrentPlayer}}`
                    }, i().createElement("div", {
                        className: ou.tooltip_trigger
                    })), i().createElement(su, {
                        className: p()(ou.commendation, ou.commendation__mutual),
                        header: R.strings.tooltips.commendations.comms_likes_sct_txt_h_05(),
                        content: R.strings.tooltips.commendations.comms_likes_sct_txt_t_05(),
                        "data-bind-if": `{{${e}.commendationStateModel.commendationState}} === '${Ke.MutualCommendation}' && !{{${e}.isCurrentPlayer}}`,
                        "data-bind-click": `model.playerList.onPlayerCommend({ vehicleId: {{${e}.vehicleId}} })`
                    }, i().createElement("div", {
                        className: ou.tooltip_trigger
                    }, i().createElement("div", {
                        "data-bind-class-toggle": `${ou.fist_left__anim}:{{${e}.commendationStateModel.isNewState}} && {{model.showCommendationAnimations}}`,
                        className: ou.fist_left
                    }), i().createElement("div", {
                        "data-bind-class-toggle": `${ou.fist_right__anim}:{{${e}.commendationStateModel.isNewState}} && {{model.showCommendationAnimations}}`,
                        className: ou.fist_right
                    }))), i().createElement(su, {
                        className: p()(ou.commendation, ou.commendation__outgoing_commend),
                        header: R.strings.tooltips.commendations.comms_likes_sct_txt_h_04(),
                        content: R.strings.tooltips.commendations.comms_likes_sct_txt_t_04(),
                        "data-bind-if": `{{${e}.commendationStateModel.commendationState}} === '${Ke.OutgoingCommendation}' && !{{${e}.isCurrentPlayer}}`
                    }, i().createElement("div", {
                        className: ou.tooltip_trigger
                    }))),
                    cu = "LiveTag_liveTag_background_51",
                    du = "LiveTag_liveTag_background__current_a1",
                    mu = "LiveTag_liveTag__wrapper_e5",
                    _u = "LiveTag_tooltip_trigger_2d",
                    Eu = "LiveTag_liveTag_tooltip_icons_20",
                    Au = "LiveTag_liveTag_tooltip_content_bd",
                    Fu = "LiveTag_liveTag_damage_7b",
                    gu = "LiveTag_liveTag_assist_db",
                    Du = "LiveTag_liveTag_block_64",
                    Cu = "LiveTag_liveTag_current__damage_81",
                    vu = "LiveTag_liveTag_current__assist_57",
                    Bu = "LiveTag_liveTag_current__block_6e",
                    pu = "LiveTag_liveTag_tooltip_background_12",
                    fu = "LiveTag_liveTag_tooltip_background__current_81",
                    bu = ({
                        path: e
                    }) => i().createElement("div", {
                        "data-bind-if": "{{model.playerList.isLiveTagsEnabled}}"
                    }, i().createElement("div", {
                        className: cu,
                        "data-bind-class-toggle": `${du}:{{${e}.isCurrentPlayer}};`,
                        "data-bind-if": `{{${e}.liveTagDamage}} || {{${e}.liveTagAssist}} || {{${e}.liveTagBlock}}`
                    }), i().createElement("div", {
                        className: mu,
                        "data-bind-if": `{{${e}.liveTagDamage}} || {{${e}.liveTagAssist}} || {{${e}.liveTagBlock}}`
                    }, i().createElement(su, {
                        contentWrapperProps: {
                            "data-bind-class-toggle": `${pu}:!{{${e}.isCurrentPlayer}};${fu}:{{${e}.isCurrentPlayer}};${pu}:!{{${e}.isCurrentPlayer}} || {{${e}.isCurrentPlayer}}`
                        },
                        header: i().createElement("div", {
                            className: Au
                        }, i().createElement("div", {
                            className: Eu
                        }, i().createElement("div", {
                            "data-bind-class-toggle": `${Fu}:!{{${e}.isCurrentPlayer}};${Cu}:{{${e}.isCurrentPlayer}}`,
                            "data-bind-if": `{{${e}.liveTagDamage}}`
                        }), i().createElement("div", {
                            "data-bind-class-toggle": `${gu}:!{{${e}.isCurrentPlayer}};${vu}:{{${e}.isCurrentPlayer}}`,
                            "data-bind-if": `{{${e}.liveTagAssist}}`
                        }), i().createElement("div", {
                            "data-bind-class-toggle": `${Du}:!{{${e}.isCurrentPlayer}};${Bu}:{{${e}.isCurrentPlayer}}`,
                            "data-bind-if": `{{${e}.liveTagBlock}}`
                        })), i().createElement("div", {
                            "data-bind-value": `{{${e}.liveTagTooltipTitle}}`
                        })),
                        content: i().createElement("div", {
                            "data-bind-value": `{{${e}.liveTagTooltipBody}}`
                        })
                    }, i().createElement("div", {
                        className: _u
                    }, i().createElement("div", {
                        "data-bind-class-toggle": `${Fu}:!{{${e}.isCurrentPlayer}};${Cu}:{{${e}.isCurrentPlayer}}`,
                        "data-bind-if": `{{${e}.liveTagDamage}}`
                    }), i().createElement("div", {
                        "data-bind-class-toggle": `${gu}:!{{${e}.isCurrentPlayer}};${vu}:{{${e}.isCurrentPlayer}}`,
                        "data-bind-if": `{{${e}.liveTagAssist}}`
                    }), i().createElement("div", {
                        "data-bind-class-toggle": `${Du}:!{{${e}.isCurrentPlayer}};${Bu}:{{${e}.isCurrentPlayer}}`,
                        "data-bind-if": `{{${e}.liveTagBlock}}`
                    }))))),
                    hu = {
                        mt_4: "UserInfo_mt_4_7c",
                        user_info: "UserInfo_user_info_e1",
                        user_info__right: "UserInfo_user_info__right_67",
                        nickname_wrapper: "UserInfo_nickname_wrapper_8b",
                        badge: "UserInfo_badge_1a",
                        suffixRibbon: "UserInfo_suffixRibbon_31",
                        userNameWrapper: "UserInfo_userNameWrapper_36",
                        userNameWrapper__colorblind: "UserInfo_userNameWrapper__colorblind_94",
                        userName: "UserInfo_userName_b1",
                        tooltip_trigger: "UserInfo_tooltip_trigger_ac",
                        clanTag: "UserInfo_clanTag_45",
                        anonymizer: "UserInfo_anonymizer_07",
                        suffixBanner: "UserInfo_suffixBanner_07",
                        suffixBadge: "UserInfo_suffixBadge_47"
                    },
                    yu = ({
                        path: e,
                        align: u
                    }) => {
                        const t = `{{${e}.userName}} !== '' ? {{${e}.userName}} : "${R.strings.ingame_gui.players_panel.unknown_name()}"`;
                        return i().createElement("div", {
                            className: p()(hu.user_info, "right" === u && hu.user_info__right)
                        },
                        "left"===u&&i().createElement("div",{style:{margin:"0 4rem",display:"flex",columnGap:"5rem"}},i().createElement("span",{"data-bind-value":`{{${e}.battles}} || ' '`,"data-bind-style-color":`{{${e}.battles_color}}`}),"\u00A0",i().createElement("span",{"data-bind-value":`{{${e}.winrate}} || ' '`,"data-bind-style-color":`{{${e}.winrate_color}}`}),"\u00A0",i().createElement("span",{"data-bind-value":`{{${e}.wn8}} || ' '`,"data-bind-style-color":`{{${e}.wn8_color}}`})),
                        "right"===u&&i().createElement("div",{style:{margin:"0 4rem",display:"flex",columnGap:"5rem"}},i().createElement("span",{"data-bind-value":`{{${e}.wn8}} || ' '`,"data-bind-style-color":`{{${e}.wn8_color}}`}),"\u00A0",i().createElement("span",{"data-bind-value":`{{${e}.winrate}} || ' '`,"data-bind-style-color":`{{${e}.winrate_color}}`}),"\u00A0",i().createElement("span",{"data-bind-value":`{{${e}.battles}} || ' '`,"data-bind-style-color":`{{${e}.battles_color}}`})),
                        i().createElement("div", {
                            className: hu.badge,
                            "data-bind-if": `{{${e}.badge.badgeID}} !== '' && {{${e}.badge.badgeID}} !== '0'`,
                            "data-bind-style-background-image-url": `"R.images.gui.maps.icons.library.badges.c_24x24.badge_" + {{${e}.badge.badgeID }}`
                        }), i().createElement("div", {
                            className: hu.nickname_wrapper
                        }, "right" === u && i().createElement("div", {
                            className: hu.suffixBanner,
                            "data-bind-if": `{{${e}.userName}} !== ''`
                        }, i().createElement("div", {
                            className: hu.suffixBadge,
                            "data-bind-if": `{{${e}.suffixBadge.badgeID}} !== '' && {{${e}.suffixBadge.badgeID}} !== '0'`,
                            "data-bind-style-background-image-url": `"R.images.gui.maps.icons.library.badges.c_24x24.badge_" + {{${e}.suffixBadge.badgeID}}`
                        }), i().createElement("div", {
                            className: hu.suffixRibbon,
                            "data-bind-if": `{{${e}.suffixBadge.badgeID}} !== '' && {{${e}.suffixBadge.badgeID}} !== '0'`,
                            "data-bind-style-background-image-url": `"R.images.gui.maps.icons.library.badges.strips.c_64x24.strip_" + {{${e}.suffixBadge.badgeID}}`
                        })),i().createElement("div", {
                            className: hu.userNameWrapper,
                            "data-bind-class-toggle": `${hu.userNameWrapper__colorblind}:{{model.playerList.isColorblind}} && {{${e}.isCurrentPlayer}}`
                        }, i().createElement("div", {
                            className: hu.hiddenUserName,
                            "data-bind-if": `{{${e}.isFakeNameVisible}} && !{{${e}.isCurrentPlayer}} && !{{model.playerList.isFogOfWarEnabled}}`,
                            "data-bind-value": `{{${e}.hiddenUserName}}`
                        }), i().createElement(su, {
                            className: hu.userName,
                            content: i().createElement("div", {
                                "data-bind-value": t
                            }),
                            "data-bind-if": `!{{${e}.isFakeNameVisible}} || {{${e}.isCurrentPlayer}}`,
                            isShort: !0,
                            reflected: "right" === u
                        }, i().createElement("div", {
                            className: hu.tooltip_trigger,
                            "data-bind-value": `{{${e}.userName}} || R.strings.ingame_gui.players_panel.unknown_name()`
                        }))), i().createElement("div", {
                            className: hu.clanTag,
                            "data-bind-if": `{{${e}.clanAbbrev}} !== '' && (!{{${e}.isFakeNameVisible}} || {{${e}.isCurrentPlayer}})`,
                            "data-bind-value": `'[' + {{${e}.clanAbbrev}} + ']'`
                        }), i().createElement(su, {
                            className: hu.anonymizer,
                            content: i().createElement("div", {
                                "data-bind-value": `{{${e}.anonymizerTooltip}}`
                            }),
                            "data-bind-if": `{{${e}.isFakeNameVisible}} && {{${e}.isCurrentPlayer}}`
                        }, i().createElement("img", {
                            className: hu.tooltip_trigger,
                            src: R.images.gui.maps.icons.library.icon_eye()
                        })), "left" === u && i().createElement("div", {
                            className: hu.suffixBanner
                        }, i().createElement("div", {
                            className: hu.suffixRibbon,
                            "data-bind-if": `{{${e}.suffixBadge.badgeID}} !== '' && {{${e}.suffixBadge.badgeID}} !== '0'`,
                            "data-bind-style-background-image-url": `"R.images.gui.maps.icons.library.badges.strips.c_64x24.strip_" + {{${e}.suffixBadge.badgeID}}`
                        }), i().createElement("div", {
                            className: hu.suffixBadge,
                            "data-bind-if": `{{${e}.suffixBadge.badgeID}} !== '' && {{${e}.suffixBadge.badgeID}} !== '0'`,
                            "data-bind-style-background-image-url": `"R.images.gui.maps.icons.library.badges.c_24x24.badge_" + {{${e}.suffixBadge.badgeID}}`
                        }))))
                    },
                    wu = "Player_right_03",
                    xu = "Player_base_9f",
                    Su = "Player_platoon_wrapper_2c",
                    Lu = "Player_kills_e8",
                    Pu = "Player_vehicleName_10",
                    Ru = "Player_chatIndicators_74",
                    Tu = "Player_vehicleContour_ae",
                    Nu = "Player_prestigeGrade_cc",
                    $u = "Player_prestigeGrade_icon_c2",
                    ku = "Player_prestigeGrade_icon_max_5d",
                    Mu = "Player_prestigeLevel_4a",
                    Iu = "Player_vehicleContour_level_d3",
                    Ou = "Player_vehicleContour_image_26",
                    Hu = "Player_killed_bg_bf",
                    Wu = "Player_vehicleNameWrapper_fe",
                    zu = "Player_voiceMuted_a1",
                    Uu = "Player_chatMuted_03",
                    Vu = "Player_vehicleContour_voiceMute_23",
                    Gu = "Player_playerStatus_37",
                    ju = "Player_commendation_e6",
                    Xu = "Player_current_bg_df",
                    qu = "Player_commendation_received_commendBack_3f",
                    Ku = "Player_commendation_received_outgoingCommendation_7a",
                    Yu = "Player_commendation_received_mutualCommendation_83",
                    Zu = "Player_base__current_c5",
                    Qu = "Player_base__isTeamKiller_e2",
                    Ju = "Player_base__colorBlind_e3",
                    et = "Player_base__killed_0f",
                    ut = "Player_vehicleContour_wrapper_dd",
                    tt = "Player_commendation__visible_a6",
                    at = "Player_platoon_wrapper__visible_ac",
                    nt = "Player_platoon_wrapper__hidden_f0",
                    rt = "Player_platoon_50",
                    it = "Player_platoon__muteIcon_36",
                    st = "Player_platoon_invite_72",
                    ot = "Player_tooltip_trigger_6a",
                    lt = "Player_platoon_invitationSent_c2",
                    ct = "Player_platoon_invitationDisabled_ee",
                    dt = "Player_platoon_acceptInvite_b9",
                    mt = "Player_inviteFromPlatoon_ef",
                    _t = "Player_base__myPlatoon_b3",
                    Et = "Player_platoon_invite__warrning_c0",
                    At = "Player_vehicleName_igr_51",
                    Ft = "Player_vehicleType_95",
                    gt = "Player_vehicleType__atSpg_19",
                    Dt = "Player_vehicleType__heavyTank_63",
                    Ct = "Player_vehicleType__lightTank_f8",
                    vt = "Player_vehicleType__mediumTank_06",
                    Bt = "Player_vehicleType__spg_13",
                    pt = "Player_vehicleContour_voiceActive_35",
                    ft = "Player_vehicleContour_voiceActive_center_e4",
                    bt = "Player_vehicleContour_voiceActive_waves_30",
                    ht = "Player_vehicleContour_voiceActive_waves__left_68",
                    yt = "Player_iron_cb",
                    wt = "Player_bronze_89",
                    xt = "Player_silver_9f",
                    St = "Player_gold_c4",
                    Lt = "Player_enamel_8f",
                    Pt = "Player_kills__disabled_66",
                    Rt = "Player_playerStatus__icon_3d",
                    Tt = "Player_playerStatus__loading_2b",
                    Nt = "Player_base__loading_1f",
                    $t = "Player_dogTag_d9",
                    kt = ["path", "className", "align"];

                function Mt() {
                    return Mt = Object.assign || function(e) {
                        for (var u = 1; u < arguments.length; u++) {
                            var t = arguments[u];
                            for (var a in t) Object.prototype.hasOwnProperty.call(t, a) && (e[a] = t[a])
                        }
                        return e
                    }, Mt.apply(this, arguments)
                }
                const It = e => [`${xu}:true || {{${e}.userName}}`, `${Zu}:{{${e}.isCurrentPlayer}}`, `${Qu}:{{${e}.isTeamKiller}}`, `${et}:{{${e}.isKilled}}`, `${_t}:{{${e}.isMyPlatoon}}`, `${Ju}:{{model.playerList.isColorblind}}`, `${Nt}:!{{${e}.isLoaded}}`].join(";"),
                    Ot = e => [`${yt}:{{${e}.prestigeEmblemModel.type}} === '${Ze.IRON}'`, `${wt}:{{${e}.prestigeEmblemModel.type}} === '${Ze.BRONZE}'`, `${xt}:{{${e}.prestigeEmblemModel.type}} === '${Ze.SILVER}'`, `${St}:{{${e}.prestigeEmblemModel.type}} === '${Ze.GOLD}'`, `${Lt}:{{${e}.prestigeEmblemModel.type}} === '${Ze.ENAMEL}'`].join(";"),
                    Ht = e => [`${Su}:{{${e}.platoon}} >= 0`, `${at}:{{${e}.platoon}} > 0 || {{${e}.isInviteSent}} || {{${e}.isInviteReceived}}`, `${nt}:!{{model.playerList.platoonsEnabled}}`].join(";"),
                    Wt = e => [`${gt}:{{${e}.vehicleType}} === '${Ye.AtSpg}'`, `${Bt}:{{${e}.vehicleType}} === '${Ye.Spg}'`, `${Dt}:{{${e}.vehicleType}} === '${Ye.HeavyTank}'`, `${Ct}:{{${e}.vehicleType}} === '${Ye.LightTank}'`, `${vt}:{{${e}.vehicleType}} === '${Ye.MediumTank}'`].join(";"),
                    zt = e => [`${ju}:!!{{${e}.commendationStateModel.commendationState}} === true`, `${tt}:{{${e}.commendationStateModel.commendationState}} === '${Ke.CommendBack}' || {{${e}.commendationStateModel.commendationState}} === '${Ke.MutualCommendation}' || {{${e}.commendationStateModel.commendationState}} === '${Ke.OutgoingCommendation}'`].join(";"),
                    Ut = e => [`${qu}:{{${e}.commendationStateModel.commendationState}} === '${Ke.CommendBack}' && {{${e}.commendationStateModel.isNewState}} && {{model.showCommendationAnimations}}`, `${Ku}:{{${e}.commendationStateModel.commendationState}} === '${Ke.OutgoingCommendation}' && {{${e}.commendationStateModel.isNewState}} && {{model.showCommendationAnimations}}`, `${Yu}:{{${e}.commendationStateModel.commendationState}} === '${Ke.MutualCommendation}' && {{${e}.commendationStateModel.isNewState}} && {{model.showCommendationAnimations}}`].join(";"),
                    Vt = e => {
                        let u = e.path,
                            t = e.className,
                            a = e.align,
                            n = void 0 === a ? "left" : a,
                            r = function(e, u) {
                                if (null == e) return {};
                                var t, a, n = {},
                                    r = Object.keys(e);
                                for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                                return n
                            }(e, kt);
                        return i().createElement("div", Mt({
                            className: p()("right" === n && wu, t)
                        }, r), i().createElement("div", {
                            "data-bind-class-toggle": It(u)
                        }, "left" === n && i().createElement(bu, {
                            path: u
                        }), i().createElement("div", {
                            "data-bind-class-toggle": `${Hu}:{{${u}.isKilled}}`,
                            "data-bind-if": `{{${u}.isKilled}} || {{${u}.isCurrentPlayer}}`
                        }), i().createElement("div", {
                            "data-bind-class-toggle": `${Xu}:{{${u}.isCurrentPlayer}};`,
                            "data-bind-if": `{{${u}.isKilled}} || {{${u}.isCurrentPlayer}}`
                        }), i().createElement("div", {
                            "data-bind-class-toggle": Ut(u)
                        }), i().createElement("div", {
                            "data-bind-class-toggle": zt(u)
                        }, "left" === n && i().createElement(lu, {
                            path: u
                        })), i().createElement("div", {
                            "data-bind-class-toggle": Ht(u)
                        }, i().createElement("div", {
                            "data-bind-if": `{{${u}.platoon}} !== 0`,
                            className: rt,
                            "data-bind-style-background-image-url": `R.images.gui.maps.icons.messenger["squad_" + ({{${u}.isMyPlatoon}} ? "gold_" : "silver_") + {{${u}.platoon}}]()`
                        }, i().createElement("img", {
                            "data-bind-if": `{{${u}.isVoiceMuted}} && {{${u}.isCurrentPlayer}}`,
                            className: it,
                            src: R.images.gui.maps.icons.platoon.members_window.muted()
                        })), i().createElement("div", {
                            "data-bind-if": `{{${u}.isInviteReceived}}`,
                            className: mt,
                            "data-bind-click": `model.playerList.onPlatoonInvite({avatarSessionID: {{${u}.avatarSessionID}}})`
                        }), "left" === n && i().createElement("div", null, i().createElement(su, {
                            className: ct,
                            content: R.strings.ingame_gui.dynamicSquad.ally.disabled(),
                            "data-bind-if": `{{${u}.isPlatoonInvitationDisabled}} && {{${u}.platoon}} === 0`
                        }, i().createElement("img", {
                            className: ot,
                            src: R.images.gui.maps.icons.battle.playerList.platoon.not_available()
                        })), i().createElement(su, {
                            className: st,
                            content: i().createElement("div", null, R.strings.ingame_gui.dynamicSquad.ally.add().replace(/%\(\w+\)s/, ""), i().createElement("div", {
                                className: Et,
                                "data-bind-if": "{{model.playerList.hasClan}} && {{model.playerList.isAnonymized}}"
                            }, R.strings.ingame_gui.dynamicSquad.ally.anonymized.clan()), i().createElement("div", {
                                className: Et,
                                "data-bind-if": "!{{model.playerList.hasClan}} && {{model.playerList.isAnonymized}}"
                            }, R.strings.ingame_gui.dynamicSquad.ally.anonymized.noClan())),
                            "data-bind-if": [`!{{${u}.isPlatoonInvitationDisabled}}`, `!{{${u}.isInviteReceived}}`, `!{{${u}.platoon}}`, `!{{${u}.isCurrentPlayer}}`, `!{{${u}.isInviteSent}}`].join(" && ")
                        }, i().createElement("div", {
                            className: ot,
                            "data-bind-click": `model.playerList.onPlatoonInvite({avatarSessionID: {{${u}.avatarSessionID}}})`
                        })), i().createElement(su, {
                            className: lt,
                            content: R.strings.ingame_gui.dynamicSquad.ally.wasSent(),
                            "data-bind-if": `!{{${u}.platoon}} && !{{${u}.isCurrentPlayer}} && !{{${u}.isPlatoonInvitationDisabled}} && {{${u}.isInviteSent}}`
                        }, i().createElement("div", {
                            className: ot
                        })), i().createElement(su, {
                            className: dt,
                            content: i().createElement("div", null, R.strings.ingame_gui.dynamicSquad.ally.received().replace(/%\(\w+\)s/, ""), i().createElement("div", {
                                className: Et,
                                "data-bind-if": "{{model.playerList.hasClan}} && {{model.playerList.isAnonymized}}"
                            }, R.strings.ingame_gui.dynamicSquad.ally.anonymized.clan()), i().createElement("div", {
                                className: Et,
                                "data-bind-if": "!{{model.playerList.hasClan}} && {{model.playerList.isAnonymized}}"
                            }, R.strings.ingame_gui.dynamicSquad.ally.anonymized.noClan())),
                            "data-bind-if": `{{${u}.isInviteReceived}} && !{{${u}.platoon}}`
                        }, i().createElement("div", {
                            className: ot,
                            "data-bind-click": `model.playerList.onPlatoonInvite({avatarSessionID: {{${u}.avatarSessionID}}})`
                        })))), i().createElement(yu, {
                            path: u,
                            align: n
                        }), i().createElement("div", {
                            className: Wu
                        },i().createElement("div", {
							className: Pu,
							"data-bind-value": `{{${u}.vehicleName}} || '...'`,
							"data-bind-style-color": `{{${u}.wn8_color}}`
						}), i().createElement("img", {
                            className: At,
                            "data-bind-if": `{{${u}.igrType}} !== 0`,
                            src: R.images.gui.maps.icons.library.premium_igr_ico()
                        })), "left" === n ? i().createElement("div", {
                            className: Ft,
                            "data-bind-style-background-image-url": `{{${u}.vehicleType}} !== '${Ye.Undefined}' && (R.images.gui.maps.icons.vehicleTypes.green[({{${u}.vehicleType}} === 'atSpg' ? 'at_spg' : {{${u}.vehicleType}})]())`
                        }) : i().createElement(i().Fragment, null, i().createElement("div", {
                            className: Ft,
                            "data-bind-if": `!{{model.playerList.isColorblind}} && {{${u}.vehicleType}} !== '${Ye.Undefined}'`,
                            "data-bind-style-background-image-url": `{{${u}.vehicleType}} !== '${Ye.Undefined}' && (R.images.gui.maps.icons.vehicleTypes.red[({{${u}.vehicleType}} === 'atSpg' ? 'at_spg' : {{${u}.vehicleType}})]())`
                        }), i().createElement("div", {
                            className: Ft,
                            "data-bind-if": "{{model.playerList.isColorblind}}",
                            "data-bind-class-toggle": Wt(u)
                        })), i().createElement("div", {
                            className: Ru
                        }, i().createElement("img", {
                            "data-bind-if": `{{${u}.isVoiceMuted}} && !{{${u}.isCurrentPlayer}}`,
                            src: R.images.gui.maps.icons.platoon.members_window.muted(),
                            className: zu
                        }), i().createElement("img", {
                            "data-bind-if": `{{${u}.isChatMuted}}`,
                            src: R.images.gui.maps.icons.platoon.members_window.muteChat(),
                            className: Uu
                        })), i().createElement("div", {
                            className: Tu
                        }, i().createElement("img", {
                            "data-bind-if": `{{${u}.isVoiceMuted}}`,
                            className: Vu,
                            src: R.images.gui.maps.icons.battle.playerList.voiceMute()
                        }), "left" === n && i().createElement("div", {
                            "data-bind-if": `{{${u}.isVoiceActive}}`,
                            className: pt
                        }, i().createElement("div", {
                            className: ft
                        }), i().createElement("div", {
                            className: bt
                        }), i().createElement("div", {
                            className: ht
                        })), i().createElement("div", {
                            className: ut
                        }, i().createElement("div", {
                            className: Ou,
                            "data-bind-style-background-image-url": `((key, folder) => (key in folder ? folder[key]() : folder.unknown()))({{${u}.vehicleContourUrl}}.replace(/-/g, "_"), R.images.gui.maps.icons.vehicle.contour)`
                        }), i().createElement("div", {
                            className: Nu,
                            "data-bind-if": `{{${u}.prestigeEmblemModel.type}} !== '${Ze.UNDEFINED}' && {{${u}.prestigeEmblemModel.level}} !== 0`,
                            "data-bind-class-toggle": Ot(u)
                        }, i().createElement("div", {
                            className: $u,
                            "data-bind-style-background-image-url": `R.images.gui.maps.icons.prestige.tab[{{${u}.prestigeEmblemModel.type}}.toLowerCase()].long["c_" + {{${u}.prestigeEmblemModel.grade}}]()`,
                            "data-bind-if": `{{${u}.prestigeEmblemModel.type}} !== '${Ze.UNDEFINED}' && {{${u}.prestigeEmblemModel.type}} !== '${Ze.MAXIMUM}'`
                        }, i().createElement("div", {
                            className: Mu,
                            "data-bind-if": `{{${u}.prestigeEmblemModel.type}} !== '${Ze.UNDEFINED}'`,
                            "data-bind-value": `{{${u}.prestigeEmblemModel.level}}`
                        })), i().createElement("img", {
                            className: ku,
                            src: R.images.gui.maps.icons.prestige.tab.prestige(),
                            "data-bind-if": `{{${u}.prestigeEmblemModel.type}} === '${Ze.MAXIMUM}'`
                        })), i().createElement("div", {
                            className: Iu,
                            "data-bind-if": `{{${u}.vehicleContourUrl}} !== ''`,
                            "data-bind-value": `['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX',][parseInt({{${u}.vehicleLevel}}) - 1]`
                        }))), i().createElement("div", {
                            "data-bind-class-toggle": `${Lu}:{{${u}.kills}} !== null;${Pt}:{{${u}.kills}} === 0; `,
                            className: Lu,
                            "data-bind-value": `{{${u}.kills}}`
                        }), i().createElement("div", {
                            className: Gu
                        }, i().createElement("img", {
                            src: R.images.gui.maps.icons.battle.playerList.inBattle(),
                            className: Rt,
                            "data-bind-if": `!{{${u}.isKilled}} && {{${u}.isLoaded}}`
                        }), i().createElement("img", {
                            src: R.images.gui.maps.icons.battle.playerList.destroyed(),
                            className: Rt,
                            "data-bind-if": `{{${u}.isKilled}} && {{${u}.isLoaded}}`
                        }), i().createElement("img", {
                            src: R.images.gui.maps.icons.battle.playerList.offline(),
                            className: p()(Rt, Tt),
                            "data-bind-if": `!{{${u}.isLoaded}}`
                        })), i().createElement("img", {
                            "data-bind-if": `{{${u}.isKiller}}`,
                            className: $t,
                            src: R.images.gui.maps.icons.battle.playerList.dogtag()
                        })))
                    },
                    Gt = {
                        mt_4: "FullStatsApp_mt_4_b7",
                        view: "FullStatsApp_view_54",
                        fullStats: "FullStatsApp_fullStats_4f",
                        fullStats_header: "FullStatsApp_fullStats_header_2c",
                        fullStats_list: "FullStatsApp_fullStats_list_81",
                        teams: "FullStatsApp_teams_4b",
                        allies: "FullStatsApp_allies_df",
                        enemies: "FullStatsApp_enemies_fe",
                        head: "FullStatsApp_head_0a",
                        title: "FullStatsApp_title_3c",
                        title_line: "FullStatsApp_title_line_c5",
                        title_line__right: "FullStatsApp_title_line__right_18",
                        title_text: "FullStatsApp_title_text_10"
                    },
                    jt = "FullStatsHeader_head_10",
                    Xt = "FullStatsHeader_head__reverse_48",
                    qt = "FullStatsHeader_commendation_icon_1f",
                    Kt = "FullStatsHeader_platoon_icon_6c",
                    Yt = "FullStatsHeader_heading_2d",
                    Zt = "FullStatsHeader_tank_icon_0d",
                    Qt = "FullStatsHeader_frag_icon_37",
                    Jt = ({
                        heading: e,
                        isAllies: u = !1
                    }) => i().createElement("div", {
                        className: u ? jt : Xt
                    }, u ? i().createElement("div", {
                        className: qt,
                        "data-bind-if": "{{model.playerList.isCommendationEnabled}}"
                    }) : null, i().createElement("img", {
                        className: Kt,
                        src: R.images.gui.maps.icons.battle.playerList.platoon.platoon_silver()
                    }), i().createElement("div", {
                        className: Yt
                    }, e), i().createElement("img", {
                        className: Zt,
                        src: R.images.gui.maps.icons.battle.playerList.tank()
                    }), i().createElement("img", {
                        className: Qt,
                        src: R.images.gui.maps.icons.battle.playerList.frag()
                    })),
                    ea = () => {
                        const e = qe.Vertical.useVerticalScrollApi();
                        (0, r.useEffect)((() => {
                            setTimeout((() => {
                                engine.synchronizeModels()
                            }), 0)
                        }), []);
                        const u = R.strings.ingame_gui.statistics.tab.line_up.title(),
                            t = R.strings.menu.loading.teams.allies(),
                            a = R.strings.menu.loading.teams.enemies();
                        return i().createElement("div", {
                            className: Gt.view
                        }, i().createElement("div", {
                            className: Gt.title
                        }, i().createElement("div", {
                            className: Gt.title_line
                        }), i().createElement("div", {
                            className: Gt.title_text
                        }, u), i().createElement("div", {
                            className: p()(Gt.title_line, Gt.title_line__right)
                        })), i().createElement("div", {
                            className: Gt.fullStats
                        }, i().createElement("div", {
                            className: Gt.fullStats_header
                        }, i().createElement(Jt, {
                            heading: t,
                            isAllies: !0
                        }), i().createElement(Jt, {
                            heading: a
                        })), i().createElement("div", {
                            className: Gt.fullStats_list
                        }, i().createElement(qe.Vertical.Default, {
                            api: e
                        }, i().createElement("div", {
                            className: Gt.teams
                        }, i().createElement("div", {
                            className: Gt.allies
                        }, i().createElement(Vt, {
                            path: "item.value",
                            className: Gt.player_list_item,
                            "data-bind-for": "index, item:{{model.playerList.allies}}"
                        })), i().createElement("div", {
                            className: Gt.enemies
                        }, i().createElement(Vt, {
                            path: "item.value",
                            className: Gt.player_list_item,
                            align: "right",
                            "data-bind-for": "index, item:{{model.playerList.enemies}} && {{model.playerList.enemies}}.length ? {{model.playerList.enemies}} : []"
                        })))))))
                    };
                var ua = t(1281);
                let ta;

                function aa(e, u) {
                    return e.replace(/\{\w+\}/g, (e => String(u[e.slice(1, -1)])))
                }! function(e) {
                    e[e.left = 0] = "left", e[e.right = 1] = "right"
                }(ta || (ta = {}));
                const na = e => e.replace(/&nbsp;/g, " "),
                    ra = (e, u, t) => {
                        if (t % 2) {
                            const t = e.pop();
                            return [...e, t + u]
                        }
                        return [...e, u]
                    },
                    ia = (e, u, t) => {
                        if (0 === t) return [u];
                        if (t % 2) return [...e, " " === u ? " " : u];
                        {
                            const t = e.pop();
                            return [...e, t + u]
                        }
                    },
                    sa = (e, u, t = ta.left) => e.split(u).reduce(t === ta.left ? ra : ia, []),
                    oa = (() => {
                        const e = new RegExp(/[\(\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3005\u3007\u3021-\u3029\u3038-\u303B\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFA6D\uFA70-\uFAD9\u{16FE2}\u{16FE3}\u{16FF0}\u{16FF1}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B738}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}]?[\u3002\uFF01\uFF0C\uFF1A\uFF1B\uFF1F]?[ %\+\x2D-9A-Za-\{\}\xA0\xC0-\u0237\u2013\u2014\u2026]+[\)\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3002\u3005\u3007\u3021-\u3029\u3038-\u303B\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFA6D\uFA70-\uFAD9\uFF01\uFF0C\uFF1A\uFF1B\uFF1F\u{16FE2}\u{16FE3}\u{16FF0}\u{16FF1}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B738}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}]?[\u3002\uFF01\uFF0C\uFF1A\uFF1B\uFF1F]?/gmu.source + "|" + /[\(\xAB\u201C\u275D][\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3005\u3007\u3021-\u3029\u3038-\u303B\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFA6D\uFA70-\uFAD9\u{16FE2}\u{16FE3}\u{16FF0}\u{16FF1}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B738}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}][\0-\u2E7F\u2E9A\u2EF4-\u2EFF\u2FD6-\u3004\u3006\u3008-\u3020\u302A-\u3037\u303C-\u33FF\u4DC0-\u4DFF\uA000-\uF8FF\uFA6E\uFA6F\uFADA-\u{16FE1}\u{16FE4}-\u{16FEF}\u{16FF2}-\u{1FFFF}\u{2A6E0}-\u{2A6FF}\u{2B739}-\u{2B73F}\u{2B81E}\u{2B81F}\u{2CEA2}-\u{2CEAF}\u{2EBE1}-\u{2F7FF}\u{2FA1E}-\u{2FFFF}\u{3134B}-\u{10FFFF}]?|[\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3005\u3007\u3021-\u3029\u3038-\u303B\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFA6D\uFA70-\uFAD9\u{16FE2}\u{16FE3}\u{16FF0}\u{16FF1}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B738}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}][\0-\u2E7F\u2E9A\u2EF4-\u2EFF\u2FD6-\u3004\u3006\u3008-\u3020\u302A-\u3037\u303C-\u33FF\u4DC0-\u4DFF\uA000-\uF8FF\uFA6E\uFA6F\uFADA-\u{16FE1}\u{16FE4}-\u{16FEF}\u{16FF2}-\u{1FFFF}\u{2A6E0}-\u{2A6FF}\u{2B739}-\u{2B73F}\u{2B81E}\u{2B81F}\u{2CEA2}-\u{2CEAF}\u{2EBE1}-\u{2F7FF}\u{2FA1E}-\u{2FFFF}\u{3134B}-\u{10FFFF}]?[\u3002\uFF01\uFF0C\uFF1A\uFF1B\uFF1F]?[\)\xBB\u201D\u275E][\u3002\uFF01\uFF0C\uFF1A\uFF1B\uFF1F]?/gmu.source + "|" + /[A-Za-z\xAA\xB5\xBA\xC0-\xD6\xD8-\xF6\xF8-\u02C1\u02C6-\u02D1\u02E0-\u02E4\u02EC\u02EE\u0370-\u0374\u0376\u0377\u037A-\u037D\u037F\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u052F\u0531-\u0556\u0559\u0560-\u0588\u05D0-\u05EA\u05EF-\u05F2\u0620-\u064A\u066E\u066F\u0671-\u06D3\u06D5\u06E5\u06E6\u06EE\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5\u07B1\u07CA-\u07EA\u07F4\u07F5\u07FA\u0800-\u0815\u081A\u0824\u0828\u0840-\u0858\u0860-\u086A\u0870-\u0887\u0889-\u088E\u08A0-\u08C9\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0980\u0985-\u098C\u098F\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC\u09DD\u09DF-\u09E1\u09F0\u09F1\u09FC\u0A05-\u0A0A\u0A0F\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32\u0A33\u0A35\u0A36\u0A38\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0\u0AE1\u0AF9\u0B05-\u0B0C\u0B0F\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32\u0B33\u0B35-\u0B39\u0B3D\u0B5C\u0B5D\u0B5F-\u0B61\u0B71\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99\u0B9A\u0B9C\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C39\u0C3D\u0C58-\u0C5A\u0C5D\u0C60\u0C61\u0C80\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDD\u0CDE\u0CE0\u0CE1\u0CF1\u0CF2\u0D04-\u0D0C\u0D0E-\u0D10\u0D12-\u0D3A\u0D3D\u0D4E\u0D54-\u0D56\u0D5F-\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E30\u0E32\u0E33\u0E40-\u0E46\u0E81\u0E82\u0E84\u0E86-\u0E8A\u0E8C-\u0EA3\u0EA5\u0EA7-\u0EB0\u0EB2\u0EB3\u0EBD\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDF\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8C\u1000-\u102A\u103F\u1050-\u1055\u105A-\u105D\u1061\u1065\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10C7\u10CD\u10D0-\u10FA\u10FC-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F5\u13F8-\u13FD\u1401-\u166C\u166F-\u167F\u1681-\u169A\u16A0-\u16EA\u16F1-\u16F8\u1700-\u1711\u171F-\u1731\u1740-\u1751\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1878\u1880-\u1884\u1887-\u18A8\u18AA\u18B0-\u18F5\u1900-\u191E\u1950-\u196D\u1970-\u1974\u1980-\u19AB\u19B0-\u19C9\u1A00-\u1A16\u1A20-\u1A54\u1AA7\u1B05-\u1B33\u1B45-\u1B4C\u1B83-\u1BA0\u1BAE\u1BAF\u1BBA-\u1BE5\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1C80-\u1C88\u1C90-\u1CBA\u1CBD-\u1CBF\u1CE9-\u1CEC\u1CEE-\u1CF3\u1CF5\u1CF6\u1CFA\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u2071\u207F\u2090-\u209C\u2102\u2107\u210A-\u2113\u2115\u2119-\u211D\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2183\u2184\u2C00-\u2CE4\u2CEB-\u2CEE\u2CF2\u2CF3\u2D00-\u2D25\u2D27\u2D2D\u2D30-\u2D67\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u2E2F\u3005\u3006\u3031-\u3035\u303B\u303C\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF\u3105-\u312F\u3131-\u318E\u31A0-\u31BF\u31F0-\u31FF\u3400-\u4DBF\u4E00-\uA48C\uA4D0-\uA4FD\uA500-\uA60C\uA610-\uA61F\uA62A\uA62B\uA640-\uA66E\uA67F-\uA69D\uA6A0-\uA6E5\uA717-\uA71F\uA722-\uA788\uA78B-\uA7CA\uA7D0\uA7D1\uA7D3\uA7D5-\uA7D9\uA7F2-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA8F2-\uA8F7\uA8FB\uA8FD\uA8FE\uA90A-\uA925\uA930-\uA946\uA960-\uA97C\uA984-\uA9B2\uA9CF\uA9E0-\uA9E4\uA9E6-\uA9EF\uA9FA-\uA9FE\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAA60-\uAA76\uAA7A\uAA7E-\uAAAF\uAAB1\uAAB5\uAAB6\uAAB9-\uAABD\uAAC0\uAAC2\uAADB-\uAADD\uAAE0-\uAAEA\uAAF2-\uAAF4\uAB01-\uAB06\uAB09-\uAB0E\uAB11-\uAB16\uAB20-\uAB26\uAB28-\uAB2E\uAB30-\uAB5A\uAB5C-\uAB69\uAB70-\uABE2\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB\uF900-\uFA6D\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40\uFB41\uFB43\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE70-\uFE74\uFE76-\uFEFC\uFF21-\uFF3A\uFF41-\uFF5A\uFF66-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC\u{10000}-\u{1000B}\u{1000D}-\u{10026}\u{10028}-\u{1003A}\u{1003C}\u{1003D}\u{1003F}-\u{1004D}\u{10050}-\u{1005D}\u{10080}-\u{100FA}\u{10280}-\u{1029C}\u{102A0}-\u{102D0}\u{10300}-\u{1031F}\u{1032D}-\u{10340}\u{10342}-\u{10349}\u{10350}-\u{10375}\u{10380}-\u{1039D}\u{103A0}-\u{103C3}\u{103C8}-\u{103CF}\u{10400}-\u{1049D}\u{104B0}-\u{104D3}\u{104D8}-\u{104FB}\u{10500}-\u{10527}\u{10530}-\u{10563}\u{10570}-\u{1057A}\u{1057C}-\u{1058A}\u{1058C}-\u{10592}\u{10594}\u{10595}\u{10597}-\u{105A1}\u{105A3}-\u{105B1}\u{105B3}-\u{105B9}\u{105BB}\u{105BC}\u{10600}-\u{10736}\u{10740}-\u{10755}\u{10760}-\u{10767}\u{10780}-\u{10785}\u{10787}-\u{107B0}\u{107B2}-\u{107BA}\u{10800}-\u{10805}\u{10808}\u{1080A}-\u{10835}\u{10837}\u{10838}\u{1083C}\u{1083F}-\u{10855}\u{10860}-\u{10876}\u{10880}-\u{1089E}\u{108E0}-\u{108F2}\u{108F4}\u{108F5}\u{10900}-\u{10915}\u{10920}-\u{10939}\u{10980}-\u{109B7}\u{109BE}\u{109BF}\u{10A00}\u{10A10}-\u{10A13}\u{10A15}-\u{10A17}\u{10A19}-\u{10A35}\u{10A60}-\u{10A7C}\u{10A80}-\u{10A9C}\u{10AC0}-\u{10AC7}\u{10AC9}-\u{10AE4}\u{10B00}-\u{10B35}\u{10B40}-\u{10B55}\u{10B60}-\u{10B72}\u{10B80}-\u{10B91}\u{10C00}-\u{10C48}\u{10C80}-\u{10CB2}\u{10CC0}-\u{10CF2}\u{10D00}-\u{10D23}\u{10E80}-\u{10EA9}\u{10EB0}\u{10EB1}\u{10F00}-\u{10F1C}\u{10F27}\u{10F30}-\u{10F45}\u{10F70}-\u{10F81}\u{10FB0}-\u{10FC4}\u{10FE0}-\u{10FF6}\u{11003}-\u{11037}\u{11071}\u{11072}\u{11075}\u{11083}-\u{110AF}\u{110D0}-\u{110E8}\u{11103}-\u{11126}\u{11144}\u{11147}\u{11150}-\u{11172}\u{11176}\u{11183}-\u{111B2}\u{111C1}-\u{111C4}\u{111DA}\u{111DC}\u{11200}-\u{11211}\u{11213}-\u{1122B}\u{11280}-\u{11286}\u{11288}\u{1128A}-\u{1128D}\u{1128F}-\u{1129D}\u{1129F}-\u{112A8}\u{112B0}-\u{112DE}\u{11305}-\u{1130C}\u{1130F}\u{11310}\u{11313}-\u{11328}\u{1132A}-\u{11330}\u{11332}\u{11333}\u{11335}-\u{11339}\u{1133D}\u{11350}\u{1135D}-\u{11361}\u{11400}-\u{11434}\u{11447}-\u{1144A}\u{1145F}-\u{11461}\u{11480}-\u{114AF}\u{114C4}\u{114C5}\u{114C7}\u{11580}-\u{115AE}\u{115D8}-\u{115DB}\u{11600}-\u{1162F}\u{11644}\u{11680}-\u{116AA}\u{116B8}\u{11700}-\u{1171A}\u{11740}-\u{11746}\u{11800}-\u{1182B}\u{118A0}-\u{118DF}\u{118FF}-\u{11906}\u{11909}\u{1190C}-\u{11913}\u{11915}\u{11916}\u{11918}-\u{1192F}\u{1193F}\u{11941}\u{119A0}-\u{119A7}\u{119AA}-\u{119D0}\u{119E1}\u{119E3}\u{11A00}\u{11A0B}-\u{11A32}\u{11A3A}\u{11A50}\u{11A5C}-\u{11A89}\u{11A9D}\u{11AB0}-\u{11AF8}\u{11C00}-\u{11C08}\u{11C0A}-\u{11C2E}\u{11C40}\u{11C72}-\u{11C8F}\u{11D00}-\u{11D06}\u{11D08}\u{11D09}\u{11D0B}-\u{11D30}\u{11D46}\u{11D60}-\u{11D65}\u{11D67}\u{11D68}\u{11D6A}-\u{11D89}\u{11D98}\u{11EE0}-\u{11EF2}\u{11FB0}\u{12000}-\u{12399}\u{12480}-\u{12543}\u{12F90}-\u{12FF0}\u{13000}-\u{1342E}\u{14400}-\u{14646}\u{16800}-\u{16A38}\u{16A40}-\u{16A5E}\u{16A70}-\u{16ABE}\u{16AD0}-\u{16AED}\u{16B00}-\u{16B2F}\u{16B40}-\u{16B43}\u{16B63}-\u{16B77}\u{16B7D}-\u{16B8F}\u{16E40}-\u{16E7F}\u{16F00}-\u{16F4A}\u{16F50}\u{16F93}-\u{16F9F}\u{16FE0}\u{16FE1}\u{16FE3}\u{17000}-\u{187F7}\u{18800}-\u{18CD5}\u{18D00}-\u{18D08}\u{1AFF0}-\u{1AFF3}\u{1AFF5}-\u{1AFFB}\u{1AFFD}\u{1AFFE}\u{1B000}-\u{1B122}\u{1B150}-\u{1B152}\u{1B164}-\u{1B167}\u{1B170}-\u{1B2FB}\u{1BC00}-\u{1BC6A}\u{1BC70}-\u{1BC7C}\u{1BC80}-\u{1BC88}\u{1BC90}-\u{1BC99}\u{1D400}-\u{1D454}\u{1D456}-\u{1D49C}\u{1D49E}\u{1D49F}\u{1D4A2}\u{1D4A5}\u{1D4A6}\u{1D4A9}-\u{1D4AC}\u{1D4AE}-\u{1D4B9}\u{1D4BB}\u{1D4BD}-\u{1D4C3}\u{1D4C5}-\u{1D505}\u{1D507}-\u{1D50A}\u{1D50D}-\u{1D514}\u{1D516}-\u{1D51C}\u{1D51E}-\u{1D539}\u{1D53B}-\u{1D53E}\u{1D540}-\u{1D544}\u{1D546}\u{1D54A}-\u{1D550}\u{1D552}-\u{1D6A5}\u{1D6A8}-\u{1D6C0}\u{1D6C2}-\u{1D6DA}\u{1D6DC}-\u{1D6FA}\u{1D6FC}-\u{1D714}\u{1D716}-\u{1D734}\u{1D736}-\u{1D74E}\u{1D750}-\u{1D76E}\u{1D770}-\u{1D788}\u{1D78A}-\u{1D7A8}\u{1D7AA}-\u{1D7C2}\u{1D7C4}-\u{1D7CB}\u{1DF00}-\u{1DF1E}\u{1E100}-\u{1E12C}\u{1E137}-\u{1E13D}\u{1E14E}\u{1E290}-\u{1E2AD}\u{1E2C0}-\u{1E2EB}\u{1E7E0}-\u{1E7E6}\u{1E7E8}-\u{1E7EB}\u{1E7ED}\u{1E7EE}\u{1E7F0}-\u{1E7FE}\u{1E800}-\u{1E8C4}\u{1E900}-\u{1E943}\u{1E94B}\u{1EE00}-\u{1EE03}\u{1EE05}-\u{1EE1F}\u{1EE21}\u{1EE22}\u{1EE24}\u{1EE27}\u{1EE29}-\u{1EE32}\u{1EE34}-\u{1EE37}\u{1EE39}\u{1EE3B}\u{1EE42}\u{1EE47}\u{1EE49}\u{1EE4B}\u{1EE4D}-\u{1EE4F}\u{1EE51}\u{1EE52}\u{1EE54}\u{1EE57}\u{1EE59}\u{1EE5B}\u{1EE5D}\u{1EE5F}\u{1EE61}\u{1EE62}\u{1EE64}\u{1EE67}-\u{1EE6A}\u{1EE6C}-\u{1EE72}\u{1EE74}-\u{1EE77}\u{1EE79}-\u{1EE7C}\u{1EE7E}\u{1EE80}-\u{1EE89}\u{1EE8B}-\u{1EE9B}\u{1EEA1}-\u{1EEA3}\u{1EEA5}-\u{1EEA9}\u{1EEAB}-\u{1EEBB}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B738}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}]?[ \):;\u2022\u3001\u3002\u300A-\u300D\uFF01\uFF0C\uFF1A\uFF1B\uFF1F]|[\(,1A-Za-\{\}\xAA\xB5\xBA\xC0-\xD6\xD8-\xF6\xF8-\u02C1\u02C6-\u02D1\u02E0-\u02E4\u02EC\u02EE\u0370-\u0374\u0376\u0377\u037A-\u037D\u037F\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u052F\u0531-\u0556\u0559\u0560-\u0588\u05D0-\u05EA\u05EF-\u05F2\u0620-\u064A\u066E\u066F\u0671-\u06D3\u06D5\u06E5\u06E6\u06EE\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5\u07B1\u07CA-\u07EA\u07F4\u07F5\u07FA\u0800-\u0815\u081A\u0824\u0828\u0840-\u0858\u0860-\u086A\u0870-\u0887\u0889-\u088E\u08A0-\u08C9\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0980\u0985-\u098C\u098F\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC\u09DD\u09DF-\u09E1\u09F0\u09F1\u09FC\u0A05-\u0A0A\u0A0F\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32\u0A33\u0A35\u0A36\u0A38\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0\u0AE1\u0AF9\u0B05-\u0B0C\u0B0F\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32\u0B33\u0B35-\u0B39\u0B3D\u0B5C\u0B5D\u0B5F-\u0B61\u0B71\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99\u0B9A\u0B9C\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C39\u0C3D\u0C58-\u0C5A\u0C5D\u0C60\u0C61\u0C80\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDD\u0CDE\u0CE0\u0CE1\u0CF1\u0CF2\u0D04-\u0D0C\u0D0E-\u0D10\u0D12-\u0D3A\u0D3D\u0D4E\u0D54-\u0D56\u0D5F-\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E30\u0E32\u0E33\u0E40-\u0E46\u0E81\u0E82\u0E84\u0E86-\u0E8A\u0E8C-\u0EA3\u0EA5\u0EA7-\u0EB0\u0EB2\u0EB3\u0EBD\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDF\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8C\u1000-\u102A\u103F\u1050-\u1055\u105A-\u105D\u1061\u1065\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10C7\u10CD\u10D0-\u10FA\u10FC-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F5\u13F8-\u13FD\u1401-\u166C\u166F-\u167F\u1681-\u169A\u16A0-\u16EA\u16F1-\u16F8\u1700-\u1711\u171F-\u1731\u1740-\u1751\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1878\u1880-\u1884\u1887-\u18A8\u18AA\u18B0-\u18F5\u1900-\u191E\u1950-\u196D\u1970-\u1974\u1980-\u19AB\u19B0-\u19C9\u1A00-\u1A16\u1A20-\u1A54\u1AA7\u1B05-\u1B33\u1B45-\u1B4C\u1B83-\u1BA0\u1BAE\u1BAF\u1BBA-\u1BE5\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1C80-\u1C88\u1C90-\u1CBA\u1CBD-\u1CBF\u1CE9-\u1CEC\u1CEE-\u1CF3\u1CF5\u1CF6\u1CFA\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u2071\u207F\u2090-\u209C\u2102\u2107\u210A-\u2113\u2115\u2119-\u211D\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2183\u2184\u2C00-\u2CE4\u2CEB-\u2CEE\u2CF2\u2CF3\u2D00-\u2D25\u2D27\u2D2D\u2D30-\u2D67\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u2E2F\u3005\u3006\u3031-\u3035\u303B\u303C\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF\u3105-\u312F\u3131-\u318E\u31A0-\u31BF\u31F0-\u31FF\u3400-\u4DBF\u4E00-\uA48C\uA4D0-\uA4FD\uA500-\uA60C\uA610-\uA61F\uA62A\uA62B\uA640-\uA66E\uA67F-\uA69D\uA6A0-\uA6E5\uA717-\uA71F\uA722-\uA788\uA78B-\uA7CA\uA7D0\uA7D1\uA7D3\uA7D5-\uA7D9\uA7F2-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA8F2-\uA8F7\uA8FB\uA8FD\uA8FE\uA90A-\uA925\uA930-\uA946\uA960-\uA97C\uA984-\uA9B2\uA9CF\uA9E0-\uA9E4\uA9E6-\uA9EF\uA9FA-\uA9FE\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAA60-\uAA76\uAA7A\uAA7E-\uAAAF\uAAB1\uAAB5\uAAB6\uAAB9-\uAABD\uAAC0\uAAC2\uAADB-\uAADD\uAAE0-\uAAEA\uAAF2-\uAAF4\uAB01-\uAB06\uAB09-\uAB0E\uAB11-\uAB16\uAB20-\uAB26\uAB28-\uAB2E\uAB30-\uAB5A\uAB5C-\uAB69\uAB70-\uABE2\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB\uF900-\uFA6D\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40\uFB41\uFB43\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE70-\uFE74\uFE76-\uFEFC\uFF21-\uFF3A\uFF41-\uFF5A\uFF66-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC\u{10000}-\u{1000B}\u{1000D}-\u{10026}\u{10028}-\u{1003A}\u{1003C}\u{1003D}\u{1003F}-\u{1004D}\u{10050}-\u{1005D}\u{10080}-\u{100FA}\u{10280}-\u{1029C}\u{102A0}-\u{102D0}\u{10300}-\u{1031F}\u{1032D}-\u{10340}\u{10342}-\u{10349}\u{10350}-\u{10375}\u{10380}-\u{1039D}\u{103A0}-\u{103C3}\u{103C8}-\u{103CF}\u{10400}-\u{1049D}\u{104B0}-\u{104D3}\u{104D8}-\u{104FB}\u{10500}-\u{10527}\u{10530}-\u{10563}\u{10570}-\u{1057A}\u{1057C}-\u{1058A}\u{1058C}-\u{10592}\u{10594}\u{10595}\u{10597}-\u{105A1}\u{105A3}-\u{105B1}\u{105B3}-\u{105B9}\u{105BB}\u{105BC}\u{10600}-\u{10736}\u{10740}-\u{10755}\u{10760}-\u{10767}\u{10780}-\u{10785}\u{10787}-\u{107B0}\u{107B2}-\u{107BA}\u{10800}-\u{10805}\u{10808}\u{1080A}-\u{10835}\u{10837}\u{10838}\u{1083C}\u{1083F}-\u{10855}\u{10860}-\u{10876}\u{10880}-\u{1089E}\u{108E0}-\u{108F2}\u{108F4}\u{108F5}\u{10900}-\u{10915}\u{10920}-\u{10939}\u{10980}-\u{109B7}\u{109BE}\u{109BF}\u{10A00}\u{10A10}-\u{10A13}\u{10A15}-\u{10A17}\u{10A19}-\u{10A35}\u{10A60}-\u{10A7C}\u{10A80}-\u{10A9C}\u{10AC0}-\u{10AC7}\u{10AC9}-\u{10AE4}\u{10B00}-\u{10B35}\u{10B40}-\u{10B55}\u{10B60}-\u{10B72}\u{10B80}-\u{10B91}\u{10C00}-\u{10C48}\u{10C80}-\u{10CB2}\u{10CC0}-\u{10CF2}\u{10D00}-\u{10D23}\u{10E80}-\u{10EA9}\u{10EB0}\u{10EB1}\u{10F00}-\u{10F1C}\u{10F27}\u{10F30}-\u{10F45}\u{10F70}-\u{10F81}\u{10FB0}-\u{10FC4}\u{10FE0}-\u{10FF6}\u{11003}-\u{11037}\u{11071}\u{11072}\u{11075}\u{11083}-\u{110AF}\u{110D0}-\u{110E8}\u{11103}-\u{11126}\u{11144}\u{11147}\u{11150}-\u{11172}\u{11176}\u{11183}-\u{111B2}\u{111C1}-\u{111C4}\u{111DA}\u{111DC}\u{11200}-\u{11211}\u{11213}-\u{1122B}\u{11280}-\u{11286}\u{11288}\u{1128A}-\u{1128D}\u{1128F}-\u{1129D}\u{1129F}-\u{112A8}\u{112B0}-\u{112DE}\u{11305}-\u{1130C}\u{1130F}\u{11310}\u{11313}-\u{11328}\u{1132A}-\u{11330}\u{11332}\u{11333}\u{11335}-\u{11339}\u{1133D}\u{11350}\u{1135D}-\u{11361}\u{11400}-\u{11434}\u{11447}-\u{1144A}\u{1145F}-\u{11461}\u{11480}-\u{114AF}\u{114C4}\u{114C5}\u{114C7}\u{11580}-\u{115AE}\u{115D8}-\u{115DB}\u{11600}-\u{1162F}\u{11644}\u{11680}-\u{116AA}\u{116B8}\u{11700}-\u{1171A}\u{11740}-\u{11746}\u{11800}-\u{1182B}\u{118A0}-\u{118DF}\u{118FF}-\u{11906}\u{11909}\u{1190C}-\u{11913}\u{11915}\u{11916}\u{11918}-\u{1192F}\u{1193F}\u{11941}\u{119A0}-\u{119A7}\u{119AA}-\u{119D0}\u{119E1}\u{119E3}\u{11A00}\u{11A0B}-\u{11A32}\u{11A3A}\u{11A50}\u{11A5C}-\u{11A89}\u{11A9D}\u{11AB0}-\u{11AF8}\u{11C00}-\u{11C08}\u{11C0A}-\u{11C2E}\u{11C40}\u{11C72}-\u{11C8F}\u{11D00}-\u{11D06}\u{11D08}\u{11D09}\u{11D0B}-\u{11D30}\u{11D46}\u{11D60}-\u{11D65}\u{11D67}\u{11D68}\u{11D6A}-\u{11D89}\u{11D98}\u{11EE0}-\u{11EF2}\u{11FB0}\u{12000}-\u{12399}\u{12480}-\u{12543}\u{12F90}-\u{12FF0}\u{13000}-\u{1342E}\u{14400}-\u{14646}\u{16800}-\u{16A38}\u{16A40}-\u{16A5E}\u{16A70}-\u{16ABE}\u{16AD0}-\u{16AED}\u{16B00}-\u{16B2F}\u{16B40}-\u{16B43}\u{16B63}-\u{16B77}\u{16B7D}-\u{16B8F}\u{16E40}-\u{16E7F}\u{16F00}-\u{16F4A}\u{16F50}\u{16F93}-\u{16F9F}\u{16FE0}\u{16FE1}\u{16FE3}\u{17000}-\u{187F7}\u{18800}-\u{18CD5}\u{18D00}-\u{18D08}\u{1AFF0}-\u{1AFF3}\u{1AFF5}-\u{1AFFB}\u{1AFFD}\u{1AFFE}\u{1B000}-\u{1B122}\u{1B150}-\u{1B152}\u{1B164}-\u{1B167}\u{1B170}-\u{1B2FB}\u{1BC00}-\u{1BC6A}\u{1BC70}-\u{1BC7C}\u{1BC80}-\u{1BC88}\u{1BC90}-\u{1BC99}\u{1D400}-\u{1D454}\u{1D456}-\u{1D49C}\u{1D49E}\u{1D49F}\u{1D4A2}\u{1D4A5}\u{1D4A6}\u{1D4A9}-\u{1D4AC}\u{1D4AE}-\u{1D4B9}\u{1D4BB}\u{1D4BD}-\u{1D4C3}\u{1D4C5}-\u{1D505}\u{1D507}-\u{1D50A}\u{1D50D}-\u{1D514}\u{1D516}-\u{1D51C}\u{1D51E}-\u{1D539}\u{1D53B}-\u{1D53E}\u{1D540}-\u{1D544}\u{1D546}\u{1D54A}-\u{1D550}\u{1D552}-\u{1D6A5}\u{1D6A8}-\u{1D6C0}\u{1D6C2}-\u{1D6DA}\u{1D6DC}-\u{1D6FA}\u{1D6FC}-\u{1D714}\u{1D716}-\u{1D734}\u{1D736}-\u{1D74E}\u{1D750}-\u{1D76E}\u{1D770}-\u{1D788}\u{1D78A}-\u{1D7A8}\u{1D7AA}-\u{1D7C2}\u{1D7C4}-\u{1D7CB}\u{1DF00}-\u{1DF1E}\u{1E100}-\u{1E12C}\u{1E137}-\u{1E13D}\u{1E14E}\u{1E290}-\u{1E2AD}\u{1E2C0}-\u{1E2EB}\u{1E7E0}-\u{1E7E6}\u{1E7E8}-\u{1E7EB}\u{1E7ED}\u{1E7EE}\u{1E7F0}-\u{1E7FE}\u{1E800}-\u{1E8C4}\u{1E900}-\u{1E943}\u{1E94B}\u{1EE00}-\u{1EE03}\u{1EE05}-\u{1EE1F}\u{1EE21}\u{1EE22}\u{1EE24}\u{1EE27}\u{1EE29}-\u{1EE32}\u{1EE34}-\u{1EE37}\u{1EE39}\u{1EE3B}\u{1EE42}\u{1EE47}\u{1EE49}\u{1EE4B}\u{1EE4D}-\u{1EE4F}\u{1EE51}\u{1EE52}\u{1EE54}\u{1EE57}\u{1EE59}\u{1EE5B}\u{1EE5D}\u{1EE5F}\u{1EE61}\u{1EE62}\u{1EE64}\u{1EE67}-\u{1EE6A}\u{1EE6C}-\u{1EE72}\u{1EE74}-\u{1EE77}\u{1EE79}-\u{1EE7C}\u{1EE7E}\u{1EE80}-\u{1EE89}\u{1EE8B}-\u{1EE9B}\u{1EEA1}-\u{1EEA3}\u{1EEA5}-\u{1EEA9}\u{1EEAB}-\u{1EEBB}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B738}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}]/gmu.source + "|" + /[\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u3005\u3007\u3021-\u3029\u3038-\u303B\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFA6D\uFA70-\uFAD9\u{16FE2}\u{16FE3}\u{16FF0}\u{16FF1}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B738}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}]/gmu.source, "gum");
                        return u => u.replace(/&nbsp;/g, " ").replace(/ /g, " ").match(e)
                    })(),
                    la = ["zh_cn", "zh_sg", "zh_tw"],
                    ca = (e, u = ta.left) => {
                        const t = R.strings.settings.LANGUAGE_CODE().toLowerCase();
                        if (la.includes(t)) return oa(e);
                        if ("ja" === t) {
                            return (0, ua.D4)().parse(e).map((e => na(e)))
                        }
                        return ((e, u = ta.left) => {
                            let t = [];
                            const a = /(?<=[a-z\xB5\xDF-\xF6\xF8-\xFF\u0101\u0103\u0105\u0107\u0109\u010B\u010D\u010F\u0111\u0113\u0115\u0117\u0119\u011B\u011D\u011F\u0121\u0123\u0125\u0127\u0129\u012B\u012D\u012F\u0131\u0133\u0135\u0137\u0138\u013A\u013C\u013E\u0140\u0142\u0144\u0146\u0148\u0149\u014B\u014D\u014F\u0151\u0153\u0155\u0157\u0159\u015B\u015D\u015F\u0161\u0163\u0165\u0167\u0169\u016B\u016D\u016F\u0171\u0173\u0175\u0177\u017A\u017C\u017E-\u0180\u0183\u0185\u0188\u018C\u018D\u0192\u0195\u0199-\u019B\u019E\u01A1\u01A3\u01A5\u01A8\u01AA\u01AB\u01AD\u01B0\u01B4\u01B6\u01B9\u01BA\u01BD-\u01BF\u01C6\u01C9\u01CC\u01CE\u01D0\u01D2\u01D4\u01D6\u01D8\u01DA\u01DC\u01DD\u01DF\u01E1\u01E3\u01E5\u01E7\u01E9\u01EB\u01ED\u01EF\u01F0\u01F3\u01F5\u01F9\u01FB\u01FD\u01FF\u0201\u0203\u0205\u0207\u0209\u020B\u020D\u020F\u0211\u0213\u0215\u0217\u0219\u021B\u021D\u021F\u0221\u0223\u0225\u0227\u0229\u022B\u022D\u022F\u0231\u0233-\u0239\u023C\u023F\u0240\u0242\u0247\u0249\u024B\u024D\u024F-\u0293\u0295-\u02AF\u0371\u0373\u0377\u037B-\u037D\u0390\u03AC-\u03CE\u03D0\u03D1\u03D5-\u03D7\u03D9\u03DB\u03DD\u03DF\u03E1\u03E3\u03E5\u03E7\u03E9\u03EB\u03ED\u03EF-\u03F3\u03F5\u03F8\u03FB\u03FC\u0430-\u045F\u0461\u0463\u0465\u0467\u0469\u046B\u046D\u046F\u0471\u0473\u0475\u0477\u0479\u047B\u047D\u047F\u0481\u048B\u048D\u048F\u0491\u0493\u0495\u0497\u0499\u049B\u049D\u049F\u04A1\u04A3\u04A5\u04A7\u04A9\u04AB\u04AD\u04AF\u04B1\u04B3\u04B5\u04B7\u04B9\u04BB\u04BD\u04BF\u04C2\u04C4\u04C6\u04C8\u04CA\u04CC\u04CE\u04CF\u04D1\u04D3\u04D5\u04D7\u04D9\u04DB\u04DD\u04DF\u04E1\u04E3\u04E5\u04E7\u04E9\u04EB\u04ED\u04EF\u04F1\u04F3\u04F5\u04F7\u04F9\u04FB\u04FD\u04FF\u0501\u0503\u0505\u0507\u0509\u050B\u050D\u050F\u0511\u0513\u0515\u0517\u0519\u051B\u051D\u051F\u0521\u0523\u0525\u0527\u0529\u052B\u052D\u052F\u0560-\u0588\u10D0-\u10FA\u10FD-\u10FF\u13F8-\u13FD\u1C80-\u1C88\u1D00-\u1D2B\u1D6B-\u1D77\u1D79-\u1D9A\u1E01\u1E03\u1E05\u1E07\u1E09\u1E0B\u1E0D\u1E0F\u1E11\u1E13\u1E15\u1E17\u1E19\u1E1B\u1E1D\u1E1F\u1E21\u1E23\u1E25\u1E27\u1E29\u1E2B\u1E2D\u1E2F\u1E31\u1E33\u1E35\u1E37\u1E39\u1E3B\u1E3D\u1E3F\u1E41\u1E43\u1E45\u1E47\u1E49\u1E4B\u1E4D\u1E4F\u1E51\u1E53\u1E55\u1E57\u1E59\u1E5B\u1E5D\u1E5F\u1E61\u1E63\u1E65\u1E67\u1E69\u1E6B\u1E6D\u1E6F\u1E71\u1E73\u1E75\u1E77\u1E79\u1E7B\u1E7D\u1E7F\u1E81\u1E83\u1E85\u1E87\u1E89\u1E8B\u1E8D\u1E8F\u1E91\u1E93\u1E95-\u1E9D\u1E9F\u1EA1\u1EA3\u1EA5\u1EA7\u1EA9\u1EAB\u1EAD\u1EAF\u1EB1\u1EB3\u1EB5\u1EB7\u1EB9\u1EBB\u1EBD\u1EBF\u1EC1\u1EC3\u1EC5\u1EC7\u1EC9\u1ECB\u1ECD\u1ECF\u1ED1\u1ED3\u1ED5\u1ED7\u1ED9\u1EDB\u1EDD\u1EDF\u1EE1\u1EE3\u1EE5\u1EE7\u1EE9\u1EEB\u1EED\u1EEF\u1EF1\u1EF3\u1EF5\u1EF7\u1EF9\u1EFB\u1EFD\u1EFF-\u1F07\u1F10-\u1F15\u1F20-\u1F27\u1F30-\u1F37\u1F40-\u1F45\u1F50-\u1F57\u1F60-\u1F67\u1F70-\u1F7D\u1F80-\u1F87\u1F90-\u1F97\u1FA0-\u1FA7\u1FB0-\u1FB4\u1FB6\u1FB7\u1FBE\u1FC2-\u1FC4\u1FC6\u1FC7\u1FD0-\u1FD3\u1FD6\u1FD7\u1FE0-\u1FE7\u1FF2-\u1FF4\u1FF6\u1FF7\u210A\u210E\u210F\u2113\u212F\u2134\u2139\u213C\u213D\u2146-\u2149\u214E\u2184\u2C30-\u2C5F\u2C61\u2C65\u2C66\u2C68\u2C6A\u2C6C\u2C71\u2C73\u2C74\u2C76-\u2C7B\u2C81\u2C83\u2C85\u2C87\u2C89\u2C8B\u2C8D\u2C8F\u2C91\u2C93\u2C95\u2C97\u2C99\u2C9B\u2C9D\u2C9F\u2CA1\u2CA3\u2CA5\u2CA7\u2CA9\u2CAB\u2CAD\u2CAF\u2CB1\u2CB3\u2CB5\u2CB7\u2CB9\u2CBB\u2CBD\u2CBF\u2CC1\u2CC3\u2CC5\u2CC7\u2CC9\u2CCB\u2CCD\u2CCF\u2CD1\u2CD3\u2CD5\u2CD7\u2CD9\u2CDB\u2CDD\u2CDF\u2CE1\u2CE3\u2CE4\u2CEC\u2CEE\u2CF3\u2D00-\u2D25\u2D27\u2D2D\uA641\uA643\uA645\uA647\uA649\uA64B\uA64D\uA64F\uA651\uA653\uA655\uA657\uA659\uA65B\uA65D\uA65F\uA661\uA663\uA665\uA667\uA669\uA66B\uA66D\uA681\uA683\uA685\uA687\uA689\uA68B\uA68D\uA68F\uA691\uA693\uA695\uA697\uA699\uA69B\uA723\uA725\uA727\uA729\uA72B\uA72D\uA72F-\uA731\uA733\uA735\uA737\uA739\uA73B\uA73D\uA73F\uA741\uA743\uA745\uA747\uA749\uA74B\uA74D\uA74F\uA751\uA753\uA755\uA757\uA759\uA75B\uA75D\uA75F\uA761\uA763\uA765\uA767\uA769\uA76B\uA76D\uA76F\uA771-\uA778\uA77A\uA77C\uA77F\uA781\uA783\uA785\uA787\uA78C\uA78E\uA791\uA793-\uA795\uA797\uA799\uA79B\uA79D\uA79F\uA7A1\uA7A3\uA7A5\uA7A7\uA7A9\uA7AF\uA7B5\uA7B7\uA7B9\uA7BB\uA7BD\uA7BF\uA7C1\uA7C3\uA7C8\uA7CA\uA7D1\uA7D3\uA7D5\uA7D7\uA7D9\uA7F6\uA7FA\uAB30-\uAB5A\uAB60-\uAB68\uAB70-\uABBF\uFB00-\uFB06\uFB13-\uFB17\uFF41-\uFF5A\u{10428}-\u{1044F}\u{104D8}-\u{104FB}\u{10597}-\u{105A1}\u{105A3}-\u{105B1}\u{105B3}-\u{105B9}\u{105BB}\u{105BC}\u{10CC0}-\u{10CF2}\u{118C0}-\u{118DF}\u{16E60}-\u{16E7F}\u{1D41A}-\u{1D433}\u{1D44E}-\u{1D454}\u{1D456}-\u{1D467}\u{1D482}-\u{1D49B}\u{1D4B6}-\u{1D4B9}\u{1D4BB}\u{1D4BD}-\u{1D4C3}\u{1D4C5}-\u{1D4CF}\u{1D4EA}-\u{1D503}\u{1D51E}-\u{1D537}\u{1D552}-\u{1D56B}\u{1D586}-\u{1D59F}\u{1D5BA}-\u{1D5D3}\u{1D5EE}-\u{1D607}\u{1D622}-\u{1D63B}\u{1D656}-\u{1D66F}\u{1D68A}-\u{1D6A5}\u{1D6C2}-\u{1D6DA}\u{1D6DC}-\u{1D6E1}\u{1D6FC}-\u{1D714}\u{1D716}-\u{1D71B}\u{1D736}-\u{1D74E}\u{1D750}-\u{1D755}\u{1D770}-\u{1D788}\u{1D78A}-\u{1D78F}\u{1D7AA}-\u{1D7C2}\u{1D7C4}-\u{1D7C9}\u{1D7CB}\u{1DF00}-\u{1DF09}\u{1DF0B}-\u{1DF1E}\u{1E922}-\u{1E943}])(\x2D)(?=[a-z\xB5\xDF-\xF6\xF8-\xFF\u0101\u0103\u0105\u0107\u0109\u010B\u010D\u010F\u0111\u0113\u0115\u0117\u0119\u011B\u011D\u011F\u0121\u0123\u0125\u0127\u0129\u012B\u012D\u012F\u0131\u0133\u0135\u0137\u0138\u013A\u013C\u013E\u0140\u0142\u0144\u0146\u0148\u0149\u014B\u014D\u014F\u0151\u0153\u0155\u0157\u0159\u015B\u015D\u015F\u0161\u0163\u0165\u0167\u0169\u016B\u016D\u016F\u0171\u0173\u0175\u0177\u017A\u017C\u017E-\u0180\u0183\u0185\u0188\u018C\u018D\u0192\u0195\u0199-\u019B\u019E\u01A1\u01A3\u01A5\u01A8\u01AA\u01AB\u01AD\u01B0\u01B4\u01B6\u01B9\u01BA\u01BD-\u01BF\u01C6\u01C9\u01CC\u01CE\u01D0\u01D2\u01D4\u01D6\u01D8\u01DA\u01DC\u01DD\u01DF\u01E1\u01E3\u01E5\u01E7\u01E9\u01EB\u01ED\u01EF\u01F0\u01F3\u01F5\u01F9\u01FB\u01FD\u01FF\u0201\u0203\u0205\u0207\u0209\u020B\u020D\u020F\u0211\u0213\u0215\u0217\u0219\u021B\u021D\u021F\u0221\u0223\u0225\u0227\u0229\u022B\u022D\u022F\u0231\u0233-\u0239\u023C\u023F\u0240\u0242\u0247\u0249\u024B\u024D\u024F-\u0293\u0295-\u02AF\u0371\u0373\u0377\u037B-\u037D\u0390\u03AC-\u03CE\u03D0\u03D1\u03D5-\u03D7\u03D9\u03DB\u03DD\u03DF\u03E1\u03E3\u03E5\u03E7\u03E9\u03EB\u03ED\u03EF-\u03F3\u03F5\u03F8\u03FB\u03FC\u0430-\u045F\u0461\u0463\u0465\u0467\u0469\u046B\u046D\u046F\u0471\u0473\u0475\u0477\u0479\u047B\u047D\u047F\u0481\u048B\u048D\u048F\u0491\u0493\u0495\u0497\u0499\u049B\u049D\u049F\u04A1\u04A3\u04A5\u04A7\u04A9\u04AB\u04AD\u04AF\u04B1\u04B3\u04B5\u04B7\u04B9\u04BB\u04BD\u04BF\u04C2\u04C4\u04C6\u04C8\u04CA\u04CC\u04CE\u04CF\u04D1\u04D3\u04D5\u04D7\u04D9\u04DB\u04DD\u04DF\u04E1\u04E3\u04E5\u04E7\u04E9\u04EB\u04ED\u04EF\u04F1\u04F3\u04F5\u04F7\u04F9\u04FB\u04FD\u04FF\u0501\u0503\u0505\u0507\u0509\u050B\u050D\u050F\u0511\u0513\u0515\u0517\u0519\u051B\u051D\u051F\u0521\u0523\u0525\u0527\u0529\u052B\u052D\u052F\u0560-\u0588\u10D0-\u10FA\u10FD-\u10FF\u13F8-\u13FD\u1C80-\u1C88\u1D00-\u1D2B\u1D6B-\u1D77\u1D79-\u1D9A\u1E01\u1E03\u1E05\u1E07\u1E09\u1E0B\u1E0D\u1E0F\u1E11\u1E13\u1E15\u1E17\u1E19\u1E1B\u1E1D\u1E1F\u1E21\u1E23\u1E25\u1E27\u1E29\u1E2B\u1E2D\u1E2F\u1E31\u1E33\u1E35\u1E37\u1E39\u1E3B\u1E3D\u1E3F\u1E41\u1E43\u1E45\u1E47\u1E49\u1E4B\u1E4D\u1E4F\u1E51\u1E53\u1E55\u1E57\u1E59\u1E5B\u1E5D\u1E5F\u1E61\u1E63\u1E65\u1E67\u1E69\u1E6B\u1E6D\u1E6F\u1E71\u1E73\u1E75\u1E77\u1E79\u1E7B\u1E7D\u1E7F\u1E81\u1E83\u1E85\u1E87\u1E89\u1E8B\u1E8D\u1E8F\u1E91\u1E93\u1E95-\u1E9D\u1E9F\u1EA1\u1EA3\u1EA5\u1EA7\u1EA9\u1EAB\u1EAD\u1EAF\u1EB1\u1EB3\u1EB5\u1EB7\u1EB9\u1EBB\u1EBD\u1EBF\u1EC1\u1EC3\u1EC5\u1EC7\u1EC9\u1ECB\u1ECD\u1ECF\u1ED1\u1ED3\u1ED5\u1ED7\u1ED9\u1EDB\u1EDD\u1EDF\u1EE1\u1EE3\u1EE5\u1EE7\u1EE9\u1EEB\u1EED\u1EEF\u1EF1\u1EF3\u1EF5\u1EF7\u1EF9\u1EFB\u1EFD\u1EFF-\u1F07\u1F10-\u1F15\u1F20-\u1F27\u1F30-\u1F37\u1F40-\u1F45\u1F50-\u1F57\u1F60-\u1F67\u1F70-\u1F7D\u1F80-\u1F87\u1F90-\u1F97\u1FA0-\u1FA7\u1FB0-\u1FB4\u1FB6\u1FB7\u1FBE\u1FC2-\u1FC4\u1FC6\u1FC7\u1FD0-\u1FD3\u1FD6\u1FD7\u1FE0-\u1FE7\u1FF2-\u1FF4\u1FF6\u1FF7\u210A\u210E\u210F\u2113\u212F\u2134\u2139\u213C\u213D\u2146-\u2149\u214E\u2184\u2C30-\u2C5F\u2C61\u2C65\u2C66\u2C68\u2C6A\u2C6C\u2C71\u2C73\u2C74\u2C76-\u2C7B\u2C81\u2C83\u2C85\u2C87\u2C89\u2C8B\u2C8D\u2C8F\u2C91\u2C93\u2C95\u2C97\u2C99\u2C9B\u2C9D\u2C9F\u2CA1\u2CA3\u2CA5\u2CA7\u2CA9\u2CAB\u2CAD\u2CAF\u2CB1\u2CB3\u2CB5\u2CB7\u2CB9\u2CBB\u2CBD\u2CBF\u2CC1\u2CC3\u2CC5\u2CC7\u2CC9\u2CCB\u2CCD\u2CCF\u2CD1\u2CD3\u2CD5\u2CD7\u2CD9\u2CDB\u2CDD\u2CDF\u2CE1\u2CE3\u2CE4\u2CEC\u2CEE\u2CF3\u2D00-\u2D25\u2D27\u2D2D\uA641\uA643\uA645\uA647\uA649\uA64B\uA64D\uA64F\uA651\uA653\uA655\uA657\uA659\uA65B\uA65D\uA65F\uA661\uA663\uA665\uA667\uA669\uA66B\uA66D\uA681\uA683\uA685\uA687\uA689\uA68B\uA68D\uA68F\uA691\uA693\uA695\uA697\uA699\uA69B\uA723\uA725\uA727\uA729\uA72B\uA72D\uA72F-\uA731\uA733\uA735\uA737\uA739\uA73B\uA73D\uA73F\uA741\uA743\uA745\uA747\uA749\uA74B\uA74D\uA74F\uA751\uA753\uA755\uA757\uA759\uA75B\uA75D\uA75F\uA761\uA763\uA765\uA767\uA769\uA76B\uA76D\uA76F\uA771-\uA778\uA77A\uA77C\uA77F\uA781\uA783\uA785\uA787\uA78C\uA78E\uA791\uA793-\uA795\uA797\uA799\uA79B\uA79D\uA79F\uA7A1\uA7A3\uA7A5\uA7A7\uA7A9\uA7AF\uA7B5\uA7B7\uA7B9\uA7BB\uA7BD\uA7BF\uA7C1\uA7C3\uA7C8\uA7CA\uA7D1\uA7D3\uA7D5\uA7D7\uA7D9\uA7F6\uA7FA\uAB30-\uAB5A\uAB60-\uAB68\uAB70-\uABBF\uFB00-\uFB06\uFB13-\uFB17\uFF41-\uFF5A\u{10428}-\u{1044F}\u{104D8}-\u{104FB}\u{10597}-\u{105A1}\u{105A3}-\u{105B1}\u{105B3}-\u{105B9}\u{105BB}\u{105BC}\u{10CC0}-\u{10CF2}\u{118C0}-\u{118DF}\u{16E60}-\u{16E7F}\u{1D41A}-\u{1D433}\u{1D44E}-\u{1D454}\u{1D456}-\u{1D467}\u{1D482}-\u{1D49B}\u{1D4B6}-\u{1D4B9}\u{1D4BB}\u{1D4BD}-\u{1D4C3}\u{1D4C5}-\u{1D4CF}\u{1D4EA}-\u{1D503}\u{1D51E}-\u{1D537}\u{1D552}-\u{1D56B}\u{1D586}-\u{1D59F}\u{1D5BA}-\u{1D5D3}\u{1D5EE}-\u{1D607}\u{1D622}-\u{1D63B}\u{1D656}-\u{1D66F}\u{1D68A}-\u{1D6A5}\u{1D6C2}-\u{1D6DA}\u{1D6DC}-\u{1D6E1}\u{1D6FC}-\u{1D714}\u{1D716}-\u{1D71B}\u{1D736}-\u{1D74E}\u{1D750}-\u{1D755}\u{1D770}-\u{1D788}\u{1D78A}-\u{1D78F}\u{1D7AA}-\u{1D7C2}\u{1D7C4}-\u{1D7C9}\u{1D7CB}\u{1DF00}-\u{1DF09}\u{1DF0B}-\u{1DF1E}\u{1E922}-\u{1E943}])/gu,
                                n = na(e);
                            return sa(n, /( )/, u).forEach((e => t = t.concat(sa(e, a, ta.left)))), t
                        })(e, u)
                    },
                    da = "FormatText_base_d0",
                    ma = ({
                        binding: e,
                        text: u = "",
                        classMix: t,
                        alignment: a = ta.left,
                        formatWithBrackets: n
                    }) => {
                        if (null === u) return console.error("FormatText was supplied with 'null'"), null;
                        const s = n && e ? aa(u, e) : u;
                        return i().createElement(r.Fragment, null, s.split("\n").map(((u, n) => i().createElement("div", {
                            className: p()(da, t),
                            key: `${u}-${n}`
                        }, ((e, u, t) => e.split(/%\((.*?)\)(?:[sd])?/g).map((e => t && e in t ? t[e] : ca(e, u))))(u, a, e).map(((e, u) => i().createElement(r.Fragment, {
                            key: `${u}-${e}`
                        }, e)))))))
                    };
                let _a;
                ! function(e) {
                    e.XP = "xp", e.Credits = "credits", e.Combined_XP = "combined", e.Event = "event", e.Clan = "clan"
                }(_a || (_a = {}));
                const Ea = "PersonalReserves_base_94",
                    Aa = "PersonalReserves_body_a8",
                    Fa = "PersonalReserves_title_a2",
                    ga = "PersonalReserves_title_line_f8",
                    Da = "PersonalReserves_title_line__right_cd",
                    Ca = "PersonalReserves_title_text_7c",
                    va = "PersonalReserves_reserves_37",
                    Ba = "PersonalReserves_notice_76",
                    pa = "PersonalReserves_notice_icon_26",
                    fa = "PersonalReserves_notice_text_7f",
                    ba = "PersonalReserves_notice_background_a9",
                    ha = "PersonalReserves_groupWrapper_3a",
                    ya = "PersonalReserves_groupWrapper_clan_7c";
                let wa, xa, Sa;
                ! function(e) {
                    e.Personal = "personal", e.Clan = "clan", e.Event = "event"
                }(wa || (wa = {})),
                function(e) {
                    e[e.Inactive = 0] = "Inactive", e[e.Active = 1] = "Active", e[e.Used = 2] = "Used"
                }(xa || (xa = {})),
                function(e) {
                    e.Gold = "booster_gold", e.Credits = "booster_credits", e.XP = "booster_xp", e.CrewXP = "booster_crew_xp", e.FreeXP = "booster_free_xp", e.FL_XP = "booster_fl_xp", e.FreeXPCrewXP = "booster_free_xp_and_crew_xp", e.FreeXPMainXP = "booster_free_xp_and_crew_xp"
                }(Sa || (Sa = {}));
                const La = {
                        [_a.XP]: R.strings.personal_reserves.activation.battleXPTitle(),
                        [_a.Credits]: R.strings.personal_reserves.activation.creditsTitle(),
                        [_a.Combined_XP]: R.strings.personal_reserves.activation.comboXPTitle(),
                        [_a.Event]: R.strings.personal_reserves.activation.frontLineXPTitle(),
                        [_a.Clan]: R.strings.personal_reserves.activation.clanBoostersTitle()
                    },
                    Pa = {
                        [_a.XP]: R.strings.personal_reserves.activation.battleXPDescription(),
                        [_a.Credits]: R.strings.personal_reserves.activation.creditsDescription(),
                        [_a.Combined_XP]: R.strings.personal_reserves.activation.comboXPDescription(),
                        [_a.Event]: R.strings.personal_reserves.activation.frontLineXPDescription(),
                        [_a.Clan]: R.strings.personal_reserves.activation.clanBoostersDescriptionCrewAndFree()
                    },
                    Ra = [R.strings.personal_reserves.activation.clanBoostersDescriptionCrewAndFree(), R.strings.personal_reserves.activation.clanBoostersDescription()],
                    Ta = {
                        base: "Counter_base_9e",
                        show: "Counter_show_be",
                        base__big: "Counter_base__big_19",
                        base__small: "Counter_base__small_3b",
                        base__empty: "Counter_base__empty_98",
                        base__animated: "Counter_base__animated_40",
                        base__hidden: "Counter_base__hidden_56",
                        hide: "Counter_hide_b6",
                        bg: "Counter_bg_74",
                        value: "Counter_value_3e",
                        value__text: "Counter_value__text_d6",
                        base__pattern: "Counter_base__pattern_71",
                        plus: "Counter_plus_15",
                        pattern: "Counter_pattern_83"
                    },
                    Na = ["size", "value", "isEmpty", "fadeInAnimation", "hide", "maximumNumber", "className"];

                function $a() {
                    return $a = Object.assign || function(e) {
                        for (var u = 1; u < arguments.length; u++) {
                            var t = arguments[u];
                            for (var a in t) Object.prototype.hasOwnProperty.call(t, a) && (e[a] = t[a])
                        }
                        return e
                    }, $a.apply(this, arguments)
                }
                const ka = e => {
                    let u = e.size,
                        t = e.value,
                        a = e.isEmpty,
                        n = e.fadeInAnimation,
                        r = e.hide,
                        s = e.maximumNumber,
                        o = e.className,
                        l = function(e, u) {
                            if (null == e) return {};
                            var t, a, n = {},
                                r = Object.keys(e);
                            for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                            return n
                        }(e, Na);
                    const c = a ? null : t,
                        d = "string" == typeof c;
                    if (c && !d && c < 0 || 0 === c) return null;
                    const m = c && !d && c > s,
                        _ = p()(Ta.base, Ta[`base__${u}`], n && Ta.base__animated, r && Ta.base__hidden, !c && Ta.base__pattern, a && Ta.base__empty, o);
                    return i().createElement("div", $a({
                        className: _
                    }, l), i().createElement("div", {
                        className: Ta.bg
                    }), i().createElement("div", {
                        className: Ta.pattern
                    }), i().createElement("div", {
                        className: p()(Ta.value, d && Ta.value__text)
                    }, m ? s : c, m && i().createElement("span", {
                        className: Ta.plus
                    }, "+")))
                };
                let Ma, Ia;
                ka.defaultProps = {
                        size: "normal",
                        fadeInAnimation: !1,
                        hide: !1,
                        maximumNumber: 99
                    },
                    function(e) {
                        e.Timer = "timer", e.Countdown = "countdown", e.Cooldown = "cooldown", e.None = "none"
                    }(Ma || (Ma = {})),
                    function(e) {
                        e.Description = "description", e.Short = "short", e.Long = "long", e.Extended = "extended"
                    }(Ia || (Ia = {}));
                var Oa = t(9916),
                    Ha = t(8613);
                const Wa = 60,
                    za = 3600,
                    Ua = 86400;
                Date.now(), Ha.Ew.getRegionalDateTime, Ha.Ew.getFormattedDateTime;

                function Va(e = 0) {
                    let u = e;
                    const t = Math.trunc(u / Ua);
                    u -= t * Ua;
                    const a = Math.trunc(u / za);
                    u -= a * za;
                    const n = Math.trunc(u / Wa);
                    return u -= n * Wa, {
                        days: t,
                        hours: a,
                        minutes: n,
                        seconds: u
                    }
                }
                const Ga = () => {},
                    ja = (e = 0, u, t = 0, a = Ga) => {
                        const n = (0, r.useState)(e),
                            i = n[0],
                            s = n[1];
                        return (0, r.useEffect)((() => {
                            if (e > 0) {
                                s(e);
                                const n = Date.now(),
                                    r = setInterval((() => {
                                        const u = e - Math.floor((Date.now() - n) / 1e3);
                                        null !== t && u <= t ? (s(t), a && a(), clearInterval(r)) : s(u)
                                    }), 1e3 * (u || (e > 120 ? Wa : 1)));
                                return () => {
                                    clearInterval(r)
                                }
                            }
                        }), [e, u, t, a]), i
                    };
                Oa.Sw.instance;
                let Xa;
                ! function(e) {
                    e.None = "None", e.Shallow = "Shallow", e.Deep = "Deep"
                }(Xa || (Xa = {}));
                Oa.Sw.instance;
                const qa = ja,
                    Ka = "Countdown_base_fe",
                    Ya = "Countdown_icon_8b",
                    Za = "Countdown_description_8d",
                    Qa = e => e.toString().padStart(2, "0"),
                    Ja = (e, u) => {
                        switch (u) {
                            case Ia.Description:
                                return ((e, u = !0) => e.days > 7 && u ? aa(R.strings.common.duration.days(), {
                                    days: e.days
                                }) : e.days >= 1 ? 0 === e.hours ? aa(R.strings.common.duration.days(), {
                                    days: e.days
                                }) : `${aa(R.strings.common.duration.days(),{days:e.days})} ${aa(R.strings.common.duration.hours(),{hours:e.hours})}` : e.hours >= 1 ? 0 === e.minutes ? aa(R.strings.common.duration.hours(), {
                                    hours: e.hours
                                }) : `${aa(R.strings.common.duration.hours(),{hours:e.hours})} ${aa(R.strings.common.duration.minutes(),{minutes:e.minutes})}` : aa(R.strings.common.duration.minutes(), {
                                    minutes: e.minutes || 1
                                }))(e);
                            case Ia.Short:
                                return `${Qa(e.minutes)}:${Qa(e.seconds)}`;
                            case Ia.Long:
                                return `${Qa(e.hours)}:${Qa(e.minutes)}:${Qa(e.seconds)}`;
                            case Ia.Extended:
                                return `${aa(R.strings.common.duration.days(),{days:e.days})} | ${Qa(e.hours)}:${Qa(e.minutes)}:${Qa(e.seconds)}`
                        }
                    },
                    en = R.images.gui.maps.icons.components.countdown,
                    un = (e, u) => {
                        const t = 2 === u ? en.big : en;
                        switch (e) {
                            case Ma.Timer:
                                return t.clock();
                            case Ma.Countdown:
                                return t.hourglass();
                            case Ma.Cooldown:
                                return t.lock()
                        }
                    };
                (0, r.memo)((({
                    duration: e,
                    icon: u = Ma.Timer,
                    style: t = Ia.Description,
                    onTimeReached: a,
                    refreshRate: n,
                    className: s = "",
                    classNames: l = {}
                }) => {
                    const c = null != n ? n : t !== Ia.Description ? 1 : void 0,
                        d = qa(e, c),
                        m = (() => {
                            const e = (0, r.useState)(o.O.view.getScale()),
                                u = e[0],
                                t = e[1];
                            return (0, r.useEffect)((() => {
                                const e = () => {
                                    t(o.O.view.getScale())
                                };
                                return window.addEventListener("resize", e), () => {
                                    window.removeEventListener("resize", e)
                                }
                            }), []), u
                        })();
                    a && a[d] && a[d]();
                    const _ = Ja(Va(d), t);
                    return i().createElement("div", {
                        className: p()(Ka, s)
                    }, u !== Ma.None && i().createElement("div", {
                        className: p()(Ya, l.icon),
                        style: {
                            backgroundImage: `url('${un(u,m)}')`
                        }
                    }), i().createElement("div", {
                        className: p()(Za, l.text)
                    }, _))
                }));
                class tn {
                    constructor(e = null) {
                        this._prices = [], null !== e && null !== e.prices && (this._prices = e.prices)
                    }
                    get length() {
                        return null !== this._prices ? this._prices.length : 0
                    }
                    isEmpty(e = 0) {
                        return 0 === this.getValue(e)
                    }
                    hasDiscount(e = 0) {
                        return this.getDiscountValue(e) > 0
                    }
                    getType(e = 0) {
                        const u = this._prices[e];
                        return u ? this._getPriceItemType(u.value.price) : ""
                    }
                    getValue(e = 0) {
                        const u = this._prices[e];
                        return u ? this._getPriceItemValue(u.value.price) : 0
                    }
                    getDefValue(e = 0) {
                        const u = this._prices[e];
                        return u ? this._getPriceItemValue(u.value.defPrice) : 0
                    }
                    getDiscountValue(e = 0) {
                        const u = this._prices[e];
                        return u ? this._getPriceItemValue(u.value.discount) : 0
                    }
                    _getPriceItemType(e) {
                        let u = "";
                        return e.some((e => (u = e.value.name, e.value.value > 0))) ? u : ""
                    }
                    _getPriceItemValue(e) {
                        let u = 0;
                        return e.some((e => (u = e.value.value, u > 0))) ? u : 0
                    }
                }
                let an;
                ! function(e) {
                    e.Personal = "personal", e.Clan = "clan", e.Event = "event"
                }(an || (an = {}));
                const nn = {
                        xp: 121e3,
                        credits: 121002,
                        combined: 121004
                    },
                    rn = {
                        booster_xp: 50,
                        booster_xp_premium: 50,
                        booster_credits: 50,
                        booster_credits_premium: 50,
                        booster_free_xp_and_crew_xp: 200,
                        booster_free_xp_and_crew_xp_premium: 200
                    };
                wa.Personal, an.Personal, wa.Event, an.Event, wa.Clan, an.Clan;
                class sn extends i().PureComponent {
                    render() {
                        let e;
                        if ("gold" === this.props.format) e = Oa.B3.GOLD;
                        else e = Oa.B3.INTEGRAL;
                        const u = Oa.Z5.getNumberFormat(this.props.value, e);
                        return void 0 !== this.props.value && void 0 !== u ? u : null
                    }
                }
                sn.defaultProps = {
                    format: "integral"
                };
                const on = {
                    base: "Currency_base_57",
                    icon: "Currency_icon_c5",
                    base__small: "Currency_base__small_af",
                    base__big: "Currency_base__big_bc",
                    base__large: "Currency_base__large_65",
                    base__extraLarge: "Currency_base__extraLarge_4d",
                    "icon__credits-small": "Currency_icon__credits-small_9b",
                    "icon__credits-big": "Currency_icon__credits-big_96",
                    "icon__credits-large": "Currency_icon__credits-large_ac",
                    "icon__credits-extraLarge": "Currency_icon__credits-extraLarge_16",
                    "icon__gold-small": "Currency_icon__gold-small_86",
                    "icon__gold-big": "Currency_icon__gold-big_15",
                    "icon__gold-large": "Currency_icon__gold-large_36",
                    "icon__gold-extraLarge": "Currency_icon__gold-extraLarge_a0",
                    "icon__crystal-small": "Currency_icon__crystal-small_27",
                    "icon__crystal-big": "Currency_icon__crystal-big_cd",
                    "icon__crystal-large": "Currency_icon__crystal-large_d3",
                    "icon__crystal-extraLarge": "Currency_icon__crystal-extraLarge_09",
                    "icon__xp-small": "Currency_icon__xp-small_a7",
                    "icon__xp-big": "Currency_icon__xp-big_97",
                    "icon__xp-large": "Currency_icon__xp-large_6b",
                    "icon__xp-extraLarge": "Currency_icon__xp-extraLarge_67",
                    "icon__freeXP-small": "Currency_icon__freeXP-small_ca",
                    "icon__freeXP-big": "Currency_icon__freeXP-big_21",
                    "icon__freeXP-large": "Currency_icon__freeXP-large_c8",
                    "icon__freeXP-extraLarge": "Currency_icon__freeXP-extraLarge_58",
                    "icon__eliteXP-small": "Currency_icon__eliteXP-small_45",
                    "icon__eliteXP-big": "Currency_icon__eliteXP-big_c0",
                    "icon__eliteXP-large": "Currency_icon__eliteXP-large_1b",
                    "icon__eliteXP-extraLarge": "Currency_icon__eliteXP-extraLarge_9b",
                    "icon__equipCoin-small": "Currency_icon__equipCoin-small_32",
                    "icon__equipCoin-big": "Currency_icon__equipCoin-big_79",
                    "icon__equipCoin-large": "Currency_icon__equipCoin-large_2c",
                    "icon__equipCoin-extraLarge": "Currency_icon__equipCoin-extraLarge_8a",
                    value: "Currency_value_e1",
                    value__freeXP: "Currency_value__freeXP_cb",
                    value__credits: "Currency_value__credits_76",
                    value__gold: "Currency_value__gold_dd",
                    value__xp: "Currency_value__xp_b0",
                    value__crystal: "Currency_value__crystal_19",
                    value__equipCoin: "Currency_value__equipCoin_d0",
                    value__eliteXP: "Currency_value__eliteXP_62",
                    value__notEnough: "Currency_value__notEnough_56",
                    stock: "Currency_stock_87",
                    stock__indent: "Currency_stock__indent_a1",
                    stock__interactive: "Currency_stock__interactive_93",
                    stockBackground: "Currency_stockBackground_82"
                };
                let ln, cn, dn;
                ! function(e) {
                    e.small = "small", e.big = "big", e.large = "large", e.extraLarge = "extraLarge"
                }(ln || (ln = {})),
                function(e) {
                    e.credits = "credits", e.gold = "gold", e.crystal = "crystal", e.xp = "xp", e.freeXP = "freeXP", e.eliteXP = "eliteXP", e.equipCoin = "equipCoin"
                }(cn || (cn = {})),
                function(e) {
                    e.Red = "RedActionBG", e.Blue = "BlueActionBG"
                }(dn || (dn = {}));
                const mn = (0, r.memo)((({
                        isDiscount: e,
                        isInteractiveDiscount: u,
                        size: t,
                        type: a,
                        value: n,
                        discountValue: r,
                        showPlus: s,
                        isEnough: o = !0,
                        stockBackgroundName: l = dn.Red,
                        className: c,
                        classNames: d
                    }) => i().createElement("span", {
                        className: p()(on.base, on[`base__${t}`], c)
                    }, i().createElement("span", {
                        className: p()(on.value, on[`value__${a}`], !o && on.value__notEnough, null == d ? void 0 : d.value)
                    }, s && n > 0 && "+", i().createElement(sn, {
                        value: n,
                        format: a === cn.gold ? "gold" : "integral"
                    })), i().createElement("span", {
                        className: p()(on.icon, on[`icon__${a}-${t}`], null == d ? void 0 : d.icon)
                    }), e && i().createElement("span", {
                        className: p()(on.stock, r && on.stock__indent, u && on.stock__interactive, null == d ? void 0 : d.stock)
                    }, i().createElement("span", {
                        className: on.stockBackground,
                        style: {
                            backgroundImage: `url(R.images.gui.maps.icons.library.${l})`
                        }
                    }), Boolean(r) && r)))),
                    _n = "Quantity_base_e7",
                    En = "Quantity_base__highlighted_3d",
                    An = "Quantity_icon_e5",
                    Fn = "Quantity_price_5f",
                    gn = "Quantity_price_icon_83",
                    Dn = "Quantity_price__discount_41",
                    Cn = ({
                        isPurchasable: e,
                        goldPrice: u = 0,
                        isDiscount: t = !1,
                        playerGold: a,
                        inDepot: n,
                        isHighlighted: r
                    }) => e && u ? i().createElement(mn, {
                        size: "small",
                        type: "gold",
                        value: u,
                        isEnough: a >= u,
                        isDiscount: t,
                        className: p()(Fn, t && Dn),
                        classNames: {
                            icon: gn
                        }
                    }) : i().createElement("div", {
                        className: p()(_n, {
                            [En]: r
                        })
                    }, i().createElement("div", {
                        className: An
                    }), n),
                    vn = {
                        base: "ReserveCard_base_37",
                        base__tooltipSize: "ReserveCard_base__tooltipSize_15",
                        base__doubleSize: "ReserveCard_base__doubleSize_fc",
                        base__clan: "ReserveCard_base__clan_64",
                        activeLight: "ReserveCard_activeLight_be",
                        boosterIcon: "ReserveCard_boosterIcon_37",
                        base__expiringToday: "ReserveCard_base__expiringToday_d3",
                        base__inactive: "ReserveCard_base__inactive_20",
                        base__disabled: "ReserveCard_base__disabled_9c",
                        timerContainer: "ReserveCard_timerContainer_65",
                        overlay: "ReserveCard_overlay_1c",
                        plusIcon: "ReserveCard_plusIcon_27",
                        base__activatedAnimation: "ReserveCard_base__activatedAnimation_aa",
                        cardFill: "ReserveCard_cardFill_15",
                        fillIn: "ReserveCard_fillIn_2b",
                        cardFill_border: "ReserveCard_cardFill_border_c0",
                        borderBrightness: "ReserveCard_borderBrightness_e5",
                        activeLight_border: "ReserveCard_activeLight_border_97",
                        timerSpark: "ReserveCard_timerSpark_2f",
                        scaleUpDown: "ReserveCard_scaleUpDown_74",
                        fadeIn: "ReserveCard_fadeIn_50",
                        base__zeroTime: "ReserveCard_base__zeroTime_c0",
                        base__gradient: "ReserveCard_base__gradient_f3",
                        disabledPattern: "ReserveCard_disabledPattern_5d",
                        overlayButton: "ReserveCard_overlayButton_c6",
                        overlayClanButton: "ReserveCard_overlayClanButton_af",
                        overlayButton_light: "ReserveCard_overlayButton_light_39",
                        overlayClanButton_light: "ReserveCard_overlayClanButton_light_02",
                        overlayButton_icon: "ReserveCard_overlayButton_icon_89",
                        cardContent: "ReserveCard_cardContent_98",
                        cardContent_quantity: "ReserveCard_cardContent_quantity_32",
                        base__active: "ReserveCard_base__active_7e",
                        cardContent_expiringQuantity: "ReserveCard_cardContent_expiringQuantity_a6",
                        cardFill_pattern: "ReserveCard_cardFill_pattern_55",
                        cardFill_borderTop: "ReserveCard_cardFill_borderTop_4f",
                        timerContainer_icon: "ReserveCard_timerContainer_icon_c9",
                        timerContainer_timer: "ReserveCard_timerContainer_timer_44",
                        bonus: "ReserveCard_bonus_d5",
                        bonusText: "ReserveCard_bonusText_b7",
                        bonusText__copied: "ReserveCard_bonusText__copied_26",
                        expiringLight: "ReserveCard_expiringLight_c0",
                        expiringIndicator: "ReserveCard_expiringIndicator_bb"
                    },
                    Bn = ["reserve", "playerGold", "activeSecondsLeft", "isDisabled", "isPurchasable", "cardSize", "onActivate", "onExpire", "onCardHover"];

                function pn() {
                    return pn = Object.assign || function(e) {
                        for (var u = 1; u < arguments.length; u++) {
                            var t = arguments[u];
                            for (var a in t) Object.prototype.hasOwnProperty.call(t, a) && (e[a] = t[a])
                        }
                        return e
                    }, pn.apply(this, arguments)
                }
                let fn;
                ! function(e) {
                    e[e.TOOLTIP = 0] = "TOOLTIP", e[e.SINGLE = 1] = "SINGLE", e[e.DOUBLE = 2] = "DOUBLE"
                }(fn || (fn = {}));
                const bn = e => {
                        let u = e.reserve,
                            t = e.playerGold,
                            a = e.activeSecondsLeft,
                            n = e.isDisabled,
                            s = e.isPurchasable,
                            o = e.cardSize,
                            l = e.onActivate,
                            c = e.onExpire,
                            d = e.onCardHover,
                            m = function(e, u) {
                                if (null == e) return {};
                                var t, a, n = {},
                                    r = Object.keys(e);
                                for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                                return n
                            }(e, Bn);
                        const _ = u.boosterID,
                            E = u.reserveType,
                            A = u.inDepot,
                            F = u.totalDuration,
                            g = void 0 === F ? 60 : F,
                            D = u.isPremium,
                            C = u.iconId,
                            v = u.price,
                            B = u.minBonus,
                            f = u.maxBonus,
                            b = u.state,
                            h = u.nextExpirationAmount,
                            y = u.isNew,
                            w = u.inDepotExpirableAmount,
                            x = u.isExpiringSoon,
                            S = w > 0,
                            L = qa(a, 1),
                            P = Math.ceil(L / g * 100),
                            T = b === xa.Active,
                            N = o === fn.TOOLTIP;
                        (0, r.useEffect)((() => {
                            T && L <= 0 && c && c()
                        }), [c, L, T]);
                        const $ = (x || S) && !T,
                            k = T && g - a < 5;
                        (0, r.useEffect)((() => {
                            k && re("personal_reserves_activation")
                        }), [k]);
                        const M = E === wa.Clan,
                            I = p()(vn.base, {
                                [vn.base__clan]: M,
                                [vn.base__event]: E === wa.Event,
                                [vn.base__premium]: D,
                                [vn.base__doubleSize]: o === fn.DOUBLE,
                                [vn.base__tooltipSize]: N,
                                [vn.base__active]: T,
                                [vn.base__disabled]: !T && n,
                                [vn.base__inactive]: !T && !n,
                                [vn.base__activatedAnimation]: k,
                                [vn.base__zeroTime]: T && L <= 0,
                                [vn.base__gradient]: T
                            }),
                            O = (0, r.useCallback)((() => {
                                T || n || re("personal_reserves_hover"), T || n || !d || d({
                                    boosterId: _
                                })
                            }), [_, T, n, d]),
                            H = (0, r.useCallback)((() => {
                                T || n || !l || l({
                                    boosterId: _
                                })
                            }), [_, l, T, n]),
                            W = Va(L),
                            z = Ja(W, W.hours ? Ia.Long : Ia.Short),
                            U = function(e, u, t) {
                                const a = e > -1 ? e : rn[t];
                                let n = `${a}`;
                                return e >= 0 && e < u && (n = `${e}-${u}`), [a > 0, n]
                            }(B, f, C),
                            V = U[0],
                            G = U[1],
                            j = new tn(v),
                            X = j.getValue(0),
                            q = j.hasDiscount(0),
                            K = (0, r.useRef)(null),
                            Y = o === fn.TOOLTIP ? "big" : "s232x174",
                            Z = `url(${!T&&M&&N?R.images.gui.maps.icons.personal_reserves.clan_icon():R.images.gui.maps.icons.quests.bonuses[Y].$dyn(C)})`,
                            Q = i().createElement(ma, {
                                text: R.strings.personal_reserves.activation.bonus(),
                                binding: {
                                    bonus: G
                                }
                            });
                        return i().createElement("div", pn({
                            className: I,
                            style: {
                                "--fillPercentage": `${P}%`
                            }
                        }, m), i().createElement("div", {
                            className: vn.contentWrapper,
                            onMouseEnter: O,
                            onClick: H
                        }, T && i().createElement(i().Fragment, null, i().createElement("div", {
                            className: vn.cardFill
                        }, i().createElement("div", {
                            className: vn.cardFill_pattern
                        }), i().createElement("div", {
                            className: vn.cardFill_borderTop
                        })), i().createElement("div", {
                            className: vn.activeLight
                        })), i().createElement("div", {
                            className: vn.overlay
                        }, M ? i().createElement("div", {
                            className: vn.overlayClanButton
                        }, i().createElement("div", {
                            className: vn.overlayClanButton_light
                        }), i().createElement(ma, {
                            text: R.strings.personal_reserves.activation.activateButtonClan()
                        })) : i().createElement("div", {
                            className: vn.overlayButton
                        }, i().createElement("div", {
                            className: vn.light
                        }), i().createElement("img", {
                            className: vn.overlayButton_icon,
                            src: R.images.gui.maps.icons.personal_reserves.activation.booster_icon(),
                            alt: ""
                        }), i().createElement(ma, {
                            text: R.strings.personal_reserves.activation.activateButton()
                        }))), n && i().createElement("div", {
                            className: vn.disabledPattern
                        }), !T && !M && x && i().createElement("div", {
                            className: vn.expiringLight
                        }), i().createElement("div", {
                            className: vn.cardContent
                        }, !M && !T && i().createElement(i().Fragment, null, i().createElement("div", {
                            className: vn.cardContent_quantity
                        }, i().createElement(Cn, {
                            isPurchasable: s,
                            goldPrice: X,
                            isDiscount: q,
                            playerGold: t,
                            inDepot: A,
                            isHighlighted: $
                        })), x && !T && i().createElement("div", {
                            className: vn.cardContent_expiringQuantity
                        }, h)), i().createElement("div", {
                            style: {
                                backgroundImage: Z
                            },
                            className: vn.boosterIcon,
                            ref: K
                        }), i().createElement("div", {
                            className: vn.timerContainer
                        }, i().createElement("div", {
                            className: vn.timerContainer_icon
                        }), i().createElement("div", {
                            className: vn.timerContainer_timer
                        }, z)), i().createElement("div", {
                            className: vn.bonus
                        }, V && i().createElement(i().Fragment, null, i().createElement("div", {
                            className: vn.bonusText
                        }, Q), i().createElement("div", {
                            className: p()(vn.bonusText, vn.bonusText__copied)
                        }, Q)))), M && !T && i().createElement("div", {
                            className: vn.plusIcon
                        })), S && y && i().createElement("div", {
                            className: vn.expiringIndicator
                        }, i().createElement(ka, {
                            isEmpty: !0
                        })))
                    },
                    hn = ["children", "contentId", "args", "onMouseEnter", "onMouseLeave", "onMouseDown", "onClick", "ignoreShowDelay", "ignoreMouseClick", "decoratorId", "isEnabled", "targetId", "onShow", "onHide"];

                function yn(e) {
                    return Object.entries(e || {}).map((([e, u]) => {
                        const t = {
                            __Type: "GFValueProxy",
                            name: e
                        };
                        switch (typeof u) {
                            case "number":
                                t.number = u;
                                break;
                            case "boolean":
                                t.bool = u;
                                break;
                            case "undefined":
                                break;
                            default:
                                t.string = u.toString()
                        }
                        return t
                    }))
                }
                const wn = (e, u, t = {}, a = 0) => {
                        viewEnv.handleViewEvent(Object.assign({
                            __Type: "GFViewEventProxy",
                            type: Oa.B0.TOOLTIP,
                            contentID: e,
                            decoratorID: u,
                            targetID: a
                        }, t))
                    },
                    xn = e => {
                        let u = e.children,
                            t = e.contentId,
                            a = e.args,
                            n = e.onMouseEnter,
                            i = e.onMouseLeave,
                            s = e.onMouseDown,
                            o = e.onClick,
                            l = e.ignoreShowDelay,
                            c = void 0 !== l && l,
                            d = e.ignoreMouseClick,
                            m = void 0 !== d && d,
                            _ = e.decoratorId,
                            E = void 0 === _ ? 0 : _,
                            A = e.isEnabled,
                            F = void 0 === A || A,
                            g = e.targetId,
                            D = void 0 === g ? 0 : g,
                            C = e.onShow,
                            v = e.onHide,
                            B = function(e, u) {
                                if (null == e) return {};
                                var t, a, n = {},
                                    r = Object.keys(e);
                                for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                                return n
                            }(e, hn);
                        const p = (0, r.useRef)({
                                timeoutId: 0,
                                isVisible: !1,
                                prevTarget: null,
                                hideTimerId: null
                            }),
                            f = (0, r.useMemo)((() => D || ((e = 1) => {
                                const u = (new Error).stack;
                                let t, a = R.invalid("resId"),
                                    n = "";
                                var r;
                                return u && (n = (null == (r = u.match(/(coui:\/\/[^\s]+\.js)/)) ? void 0 : r[0]) || "", t = u.split("\n")[e].split(".js")[0].split("/").pop() || "", window.__feature && window.__feature !== t && window.subViews[t] && (a = window.subViews[t].id)), {
                                    callerUrl: n,
                                    caller: t,
                                    stack: u,
                                    resId: a
                                }
                            })().resId), [D]),
                            b = (0, r.useCallback)((() => {
                                p.current.isVisible && p.current.timeoutId || (wn(t, E, {
                                    isMouseEvent: !0,
                                    on: !0,
                                    arguments: yn(a)
                                }, f), C && C(), p.current.isVisible = !0)
                            }), [t, E, a, f, C]),
                            h = (0, r.useCallback)((() => {
                                if (p.current.isVisible || p.current.timeoutId) {
                                    const e = p.current.timeoutId;
                                    e > 0 && (clearTimeout(e), p.current.timeoutId = 0), wn(t, E, {
                                        on: !1
                                    }, f), p.current.isVisible && v && v(), p.current.isVisible = !1
                                }
                            }), [t, E, f, v]),
                            y = (0, r.useCallback)((e => {
                                p.current.isVisible && (p.current.prevTarget = document.elementFromPoint(e.clientX, e.clientY), p.current.hideTimerId = window.setTimeout((() => {
                                    const u = document.elementFromPoint(e.clientX, e.clientY);
                                    u && !u.isSameNode(p.current.prevTarget) && h()
                                }), 200))
                            }), []);
                        (0, r.useEffect)((() => {
                            const e = p.current.hideTimerId;
                            return document.addEventListener("wheel", y, {
                                capture: !0
                            }), () => {
                                document.removeEventListener("wheel", y, {
                                    capture: !0
                                }), e && window.clearTimeout(e)
                            }
                        }), []), (0, r.useEffect)((() => {
                            !1 === F && h()
                        }), [F, h]), (0, r.useEffect)((() => (window.addEventListener("mouseleave", h), () => {
                            window.removeEventListener("mouseleave", h), h()
                        })), [h]);
                        return F ? (0, r.cloneElement)(u, Object.assign({
                            onMouseEnter: (w = u.props.onMouseEnter, e => {
                                e.clientX === window.innerWidth && e.clientY === window.innerHeight || (p.current.timeoutId = window.setTimeout(b, c ? 100 : 400), n && n(e), w && w(e))
                            }),
                            onMouseLeave: (e => u => {
                                h(), null == i || i(u), null == e || e(u)
                            })(u.props.onMouseLeave),
                            onClick: (e => u => {
                                !1 === m && h(), null == o || o(u), null == e || e(u)
                            })(u.props.onClick),
                            onMouseDown: (e => u => {
                                !1 === m && h(), null == s || s(u), null == e || e(u)
                            })(u.props.onMouseDown)
                        }, B)) : u;
                        var w
                    },
                    Sn = ["children", "body", "header", "note", "alert", "args"];

                function Ln() {
                    return Ln = Object.assign || function(e) {
                        for (var u = 1; u < arguments.length; u++) {
                            var t = arguments[u];
                            for (var a in t) Object.prototype.hasOwnProperty.call(t, a) && (e[a] = t[a])
                        }
                        return e
                    }, Ln.apply(this, arguments)
                }
                const Pn = R.views.common.tooltip_window.simple_tooltip_content,
                    Rn = e => {
                        let u = e.children,
                            t = e.body,
                            a = e.header,
                            n = e.note,
                            s = e.alert,
                            o = e.args,
                            l = function(e, u) {
                                if (null == e) return {};
                                var t, a, n = {},
                                    r = Object.keys(e);
                                for (a = 0; a < r.length; a++) t = r[a], u.indexOf(t) >= 0 || (n[t] = e[t]);
                                return n
                            }(e, Sn);
                        const c = (0, r.useMemo)((() => {
                            const e = Object.assign({}, o, {
                                body: t,
                                header: a,
                                note: n,
                                alert: s
                            });
                            for (const u in e) void 0 === e[u] && delete e[u];
                            return e
                        }), [s, t, a, n, o]);
                        return i().createElement(xn, Ln({
                            contentId: (d = null == o ? void 0 : o.hasHtmlContent, d ? Pn.SimpleTooltipHtmlContent("resId") : Pn.SimpleTooltipContent("resId")),
                            decoratorId: R.views.common.tooltip_window.tooltip_window.TooltipWindow("resId"),
                            args: c
                        }, l), u);
                        var d
                    },
                    Tn = ({
                        behaviour: e,
                        children: u,
                        item: t,
                        category: a,
                        activeSecondsLeft: n,
                        hasActiveGroupItems: r
                    }) => {
                        if (e === In.LOBBY) {
                            if (!t.isPremium && t.state !== xa.Active && r) return i().createElement(Rn, {
                                body: R.strings.personal_reserves.disabledReserveTooltip.text()
                            }, u);
                            if (0 === t.inDepot && !t.isPremium && t.reserveType !== wa.Clan) return i().createElement(xn, {
                                contentId: R.views.common.personal_reserves.ReservesDisabledTooltip("resId")
                            }, u);
                            const e = t.reserveType === wa.Clan,
                                n = t.boosterID > 0 ? t.boosterID : nn[a];
                            return e && !r ? u : i().createElement(xn, {
                                contentId: R.views.lobby.personal_reserves.BoosterTooltip("resId"),
                                args: {
                                    specialAlias: e ? "clanReserveInfo" : "boostersBoosterInfo",
                                    boosterId: n
                                }
                            }, u)
                        }
                        if (e === In.BATTLE) {
                            if (t.state !== xa.Active && r) return i().createElement(Rn, {
                                body: R.strings.personal_reserves.disabledReserveTooltip.text()
                            }, u);
                            if (t.state === xa.Active && n <= 0) return i().createElement(Rn, {
                                body: R.strings.personal_reserves.finishedReserveTooltip.text()
                            }, u);
                            if (0 === t.inDepot) return t.isPremium ? i().createElement(Rn, {
                                body: R.strings.personal_reserves.noPaidReserveTooltip.text()
                            }, u) : i().createElement(xn, {
                                contentId: R.views.common.personal_reserves.ReservesDisabledTooltip("resId")
                            }, u)
                        }
                        return u
                    },
                    Nn = "ReserveGroup_base_86",
                    $n = "ReserveGroup_header_58",
                    kn = "ReserveGroup_header_title_e4",
                    Mn = "ReserveGroup_header_description_03";
                let In;
                ! function(e) {
                    e[e.LOBBY = 0] = "LOBBY", e[e.BATTLE = 1] = "BATTLE"
                }(In || (In = {}));
                const On = ({
                        behaviour: e,
                        category: u,
                        className: t,
                        gold: a = 0,
                        items: n,
                        onActivate: s,
                        onCardHover: o = z
                    }) => {
                        const l = (0, r.useReducer)((e => !e), !1)[1],
                            c = n.some((e => (null == e ? void 0 : e.inactivationTime) > 0)),
                            d = 1 === n.length,
                            m = u === _a.Clan,
                            _ = La[u],
                            E = Math.ceil(n.length / 2);
                        return i().createElement(i().Fragment, null, Array(E).fill(0).map(((r, E) => {
                            const A = m ? Ra[E] : Pa[u],
                                F = n.slice(2 * E, 2 * (E + 1));
                            return i().createElement("div", {
                                id: `block-${u}`,
                                key: `${u}-${E}`,
                                className: t
                            }, i().createElement("div", {
                                className: Nn,
                                key: u + "-" + E
                            }, i().createElement("div", {
                                className: $n
                            }, i().createElement("div", {
                                className: kn
                            }, _), i().createElement("div", {
                                className: Mn
                            }, A)), F.map(((t, r) => {
                                const m = Math.max(0, Math.floor((1e3 * t.inactivationTime - Date.now()) / 1e3));
                                let _ = !1;
                                u === _a.Clan ? _ = m <= 0 && c : e === In.BATTLE ? t.state !== xa.Active && (_ = 0 === t.inDepot || c) : t.isPremium || t.state === xa.Active || (_ = 0 === t.inDepot || c && t.inactivationTime <= 0);
                                const E = e !== In.BATTLE && (t.isPremium && t.state !== xa.Active && 0 === t.inDepot);
                                return i().createElement(Tn, {
                                    key: r,
                                    behaviour: e,
                                    item: t,
                                    category: u,
                                    activeSecondsLeft: m,
                                    hasActiveGroupItems: n.length > 1 && c
                                }, i().createElement(bn, {
                                    reserve: t,
                                    playerGold: a,
                                    activeSecondsLeft: m,
                                    isDisabled: _,
                                    isPurchasable: E,
                                    cardSize: d ? fn.DOUBLE : fn.SINGLE,
                                    onActivate: s,
                                    onExpire: l,
                                    onCardHover: o
                                }))
                            }))))
                        })))
                    },
                    Hn = (0, W.Pi)((({
                        category: e,
                        className: u
                    }) => {
                        const t = J(),
                            a = t.model,
                            n = t.controls,
                            r = a.computes.getReserveCategoryItems(e),
                            s = n.onBoosterActivate;
                        return i().createElement(On, {
                            behaviour: In.BATTLE,
                            category: e,
                            className: u,
                            onActivate: s,
                            items: r
                        })
                    })),
                    Wn = (0, W.Pi)((() => {
                        const e = J().model.computes.getReserveCategoryNames(),
                            u = R.strings.personal_reserves.battleView.title();
                        return i().createElement("div", {
                            className: Ea
                        }, i().createElement("div", {
                            className: Aa
                        }, i().createElement("div", {
                            className: Fa
                        }, i().createElement("div", {
                            className: ga
                        }), i().createElement("div", {
                            className: Ca
                        }, u), i().createElement("div", {
                            className: p()(ga, Da)
                        })), i().createElement("div", {
                            className: va
                        }, e.map((e => {
                            const u = e === _a.Clan;
                            return i().createElement(Hn, {
                                key: e,
                                category: e,
                                className: p()(ha, u && ya)
                            })
                        })))), i().createElement("div", {
                            className: Ba
                        }, i().createElement("div", {
                            className: pa
                        }), i().createElement("div", {
                            className: fa
                        }, i().createElement(ma, {
                            text: R.strings.personal_reserves.battleView.notice()
                        })), i().createElement("div", {
                            className: ba
                        })))
                    })),
                    zn = "TabViewApp_base_85",
                    Un = {
                        [H.Reserves]: i().createElement(Wn, null),
                        [H.Stats]: i().createElement(ea, null)
                    },
                    Vn = (0, W.Pi)((() => {
                        const e = J().model.tabSelection.get(),
                            u = e in Un ? e : H.Stats;
                        return i().createElement("div", {
                            className: zn
                        }, Un[u])
                    }));
                engine.whenReady.then((() => {
                    O().render(i().createElement(Q, null, i().createElement(M, null, i().createElement(Vn, null))), document.getElementById("root"))
                }))
            },
            7363: e => {
                "use strict";
                e.exports = React
            },
            1533: e => {
                "use strict";
                e.exports = ReactDOM
            }
        },
        __webpack_module_cache__ = {},
        deferred;

    function __webpack_require__(e) {
        var u = __webpack_module_cache__[e];
        if (void 0 !== u) return u.exports;
        var t = __webpack_module_cache__[e] = {
            exports: {}
        };
        return __webpack_modules__[e](t, t.exports, __webpack_require__), t.exports
    }
    __webpack_require__.m = __webpack_modules__, deferred = [], __webpack_require__.O = (e, u, t, a) => {
        if (!u) {
            var n = 1 / 0;
            for (o = 0; o < deferred.length; o++) {
                for (var [u, t, a] = deferred[o], r = !0, i = 0; i < u.length; i++)(!1 & a || n >= a) && Object.keys(__webpack_require__.O).every((e => __webpack_require__.O[e](u[i]))) ? u.splice(i--, 1) : (r = !1, a < n && (n = a));
                if (r) {
                    deferred.splice(o--, 1);
                    var s = t();
                    void 0 !== s && (e = s)
                }
            }
            return e
        }
        a = a || 0;
        for (var o = deferred.length; o > 0 && deferred[o - 1][2] > a; o--) deferred[o] = deferred[o - 1];
        deferred[o] = [u, t, a]
    }, __webpack_require__.n = e => {
        var u = e && e.__esModule ? () => e.default : () => e;
        return __webpack_require__.d(u, {
            a: u
        }), u
    }, __webpack_require__.d = (e, u) => {
        for (var t in u) __webpack_require__.o(u, t) && !__webpack_require__.o(e, t) && Object.defineProperty(e, t, {
            enumerable: !0,
            get: u[t]
        })
    }, __webpack_require__.g = function() {
        if ("object" == typeof globalThis) return globalThis;
        try {
            return this || new Function("return this")()
        } catch (e) {
            if ("object" == typeof window) return window
        }
    }(), __webpack_require__.o = (e, u) => Object.prototype.hasOwnProperty.call(e, u), __webpack_require__.r = e => {
        "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, {
            value: "Module"
        }), Object.defineProperty(e, "__esModule", {
            value: !0
        })
    }, __webpack_require__.j = 812, (() => {
        var e = {
            812: 0
        };
        __webpack_require__.O.j = u => 0 === e[u];
        var u = (u, t) => {
                var a, n, [r, i, s] = t,
                    o = 0;
                if (r.some((u => 0 !== e[u]))) {
                    for (a in i) __webpack_require__.o(i, a) && (__webpack_require__.m[a] = i[a]);
                    if (s) var l = s(__webpack_require__)
                }
                for (u && u(t); o < r.length; o++) n = r[o], __webpack_require__.o(e, n) && e[n] && e[n][0](), e[n] = 0;
                return __webpack_require__.O(l)
            },
            t = self.webpackChunkgameface = self.webpackChunkgameface || [];
        t.forEach(u.bind(null, 0)), t.push = u.bind(null, t.push.bind(t))
    })();
    var __webpack_exports__ = __webpack_require__.O(void 0, [532], (() => __webpack_require__(5705)));
    __webpack_exports__ = __webpack_require__.O(__webpack_exports__)
})();