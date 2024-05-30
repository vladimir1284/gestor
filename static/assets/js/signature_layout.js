class HandWritingCtl {
  LW = 0;
  canvas = null;
  ctx = null;

  paths = [];
  lastPath = null;
  lastQ = null;

  lastPoint = null;

  initCanvas = (canvas) => {
    this.canvas = canvas;
    canvas.addEventListener("mousedown", this.onMouseDown, false);
    canvas.addEventListener("touchstart", this.onMouseDown, false);
    this.startCtx();
  };

  setSize = (W, H) => {
    if (!this.canvas) {
      throw new Error("Not canvas was initialize");
    }
    this.canvas.width = W;
    this.canvas.height = H;

    this.LW = Math.max(Math.min(W, H) / 200, 1.2);
    this.startCtx();
  };

  startCtx = () => {
    if (!this.canvas) {
      throw new Error("Not canvas was initialize");
    }

    this.ctx = this.canvas.getContext("2d");
    if (!this.ctx) {
      throw new Error("Failed to get canvas' 2d context");
    }

    this.clearCanvas();

    this.ctx.strokeStyle = "#334";
    this.ctx.lineWidth = this.LW;
    this.ctx.lineCap = "round";

    this.redrawPaths();
  };

  clearCanvas = () => {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    const fxy = this.getCoords({
      x: 0.05,
      y: 0.8,
    });
    const txy = this.getCoords({
      x: 0.95,
      y: 0.8,
    });

    this.ctx.beginPath();
    this.ctx.strokeStyle = "#111";
    this.ctx.lineWidth = this.LW * 1.3;
    this.ctx.lineCap = "round";
    this.ctx.moveTo(fxy.x, fxy.y);
    this.ctx.lineTo(txy.x, txy.y);
    this.stroke();
  };

  clear = () => {
    this.paths = [];
    this.lastPath = null;
    this.lastQ = null;

    this.lastPoint = null;

    this.clearCanvas();
  };

  onMouseDown = (e) => {
    e.preventDefault();
    e.stopPropagation();

    this.canvas.addEventListener("mousemove", this.onMouseMove, false);
    this.canvas.addEventListener("mouseup", this.onMouseUp, false);
    this.canvas.addEventListener("touchmove", this.onMouseMove, false);
    this.canvas.addEventListener("touchend", this.onMouseUp, false);

    document.body.addEventListener("mouseup", this.onMouseUp, false);
    document.body.addEventListener("touchend", this.onMouseUp, false);

    this.lastPoint = this.getPoint(e);
    this.begin();
    this.move(this.lastPoint);

    // Create new path
    this.lastPath = [];
    this.paths.push(this.lastPath);

    // Create the first curve
    this.lastQ = {
      from: this.lastPoint,
      to: null,
      ctl: null,
    };
    this.lastPath.push(this.lastQ);
  };

  onMouseMove = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const point = this.getPoint(e);

    const to = {
      x: (this.lastPoint.x + point.x) / 2,
      y: (this.lastPoint.y + point.y) / 2,
    };

    this.quadratic(to, this.lastPoint);
    this.stroke();
    this.begin();
    this.move(to);

    // Complete last curve
    this.lastQ.to = to;
    this.lastQ.ctl = this.lastPoint;
    this.lastPoint = point;

    // Create a new curve and add it to the path
    this.lastQ = {
      from: to,
      to: null,
      ctl: null,
    };
    this.lastPath.push(this.lastQ);
  };

  onMouseUp = () => {
    this.removeEventListeners();
    this.stroke();
  };

  removeEventListeners = () => {
    this.canvas.removeEventListener("mousemove", this.onMouseMove, false);
    this.canvas.removeEventListener("mouseup", this.onMouseUp, false);
    this.canvas.removeEventListener("touchmove", this.onMouseMove, false);
    this.canvas.removeEventListener("touchend", this.onMouseUp, false);
    document.body.removeEventListener("mouseup", this.onMouseUp, false);
    document.body.removeEventListener("touchend", this.onMouseUp, false);
  };

  getPoint = (e) => {
    var x, y;

    if (e.changedTouches && e.changedTouches[0]) {
      x = e.changedTouches[0].pageX;
      y = e.changedTouches[0].pageY;
    } else {
      x = e.pageX;
      y = e.pageY;
    }

    const rect = this.canvas.getBoundingClientRect();

    return {
      x: (x - rect.x) / rect.width,
      y: (y - rect.y) / rect.height,
    };
  };

  getCoords = (point) => {
    const rect = this.canvas.getBoundingClientRect();

    return {
      x: point.x * rect.width,
      y: point.y * rect.height,
    };
  };

  begin = () => {
    this.ctx.beginPath();
    this.ctx.strokeStyle = "#334";
    this.ctx.lineWidth = this.LW;
    this.ctx.lineCap = "round";
  };

  move = (point) => {
    const xy = this.getCoords(point);
    this.ctx.moveTo(xy.x, xy.y);
  };

  quadratic = (to, ctl) => {
    const toXY = this.getCoords(to);
    const ctlXY = this.getCoords(ctl);
    this.ctx.quadraticCurveTo(ctlXY.x, ctlXY.y, toXY.x, toXY.y);
  };

  stroke = () => {
    this.ctx.stroke();
  };

  getMaxMin = () => {
    let MM = {
      left: null,
      right: null,
      top: null,
      bottom: null,
    };
    for (let path of this.paths) {
      for (let q of path) {
        // from
        if (q.from) {
          if (!MM.left || MM.left > q.from.x) {
            MM.left = q.from.x;
          }
          if (!MM.right || MM.right < q.from.x) {
            MM.right = q.from.x;
          }
          if (!MM.top || MM.top > q.from.y) {
            MM.top = q.from.y;
          }
          if (!MM.bottom || MM.bottom < q.from.y) {
            MM.bottom = q.from.y;
          }
        }
        // to
        if (q.to) {
          if (!MM.left || MM.left > q.to.x) {
            MM.left = q.to.x;
          }
          if (!MM.right || MM.right < q.to.x) {
            MM.right = q.to.x;
          }
          if (!MM.top || MM.top > q.to.y) {
            MM.top = q.to.y;
          }
          if (!MM.bottom || MM.bottom < q.to.y) {
            MM.bottom = q.to.y;
          }
        }
        // ctl
        if (q.ctl) {
          if (!MM.left || MM.left > q.ctl.x) {
            MM.left = q.ctl.x;
          }
          if (!MM.right || MM.right < q.ctl.x) {
            MM.right = q.ctl.x;
          }
          if (!MM.top || MM.top > q.ctl.y) {
            MM.top = q.ctl.y;
          }
          if (!MM.bottom || MM.bottom < q.ctl.y) {
            MM.bottom = q.ctl.y;
          }
        }
      }
    }
    return MM;
  };

  normalizePoint = (p, s) => {
    p.x = p.x * s;
    p.y = p.y * s;
  };

  normalize = (s) => {
    for (let path of this.paths) {
      for (let q of path) {
        // from
        if (q.from) {
          this.normalizePoint(q.from, s);
        }
        // to
        if (q.to) {
          this.normalizePoint(q.to, s);
        }
        // ctl
        if (q.ctl) {
          this.normalizePoint(q.ctl, s);
        }
      }
    }
  };

  buetify = () => {
    // MaxMin
    const MM = this.getMaxMin();
    // Margin
    const M = 0.05;
    // Scales
    const SW = 1 / (MM.right - MM.left);
    const SH = 1 / (MM.bottom - MM.top);
    const S = Math.min(SW, SH);
    this.normalize(2);
  };

  drawQ = (q) => {
    if (!q.from || !q.to || !q.ctl) return;
    this.move(q.from);
    this.quadratic(q.to, q.ctl);
  };

  redrawPaths = () => {
    for (let path of this.paths) {
      this.begin();
      for (let q of path) {
        this.drawQ(q);
      }
      this.stroke();
    }
  };

  capture = () => {
    // this.buetify();
    const W = this.canvas.width;
    const H = this.canvas.height;
    this.setSize(500, 300);
    const data = this.canvas.toDataURL("image/png");
    this.setSize(W, H);

    return data;
  };

  empty = () => {
    return this.paths.length == 0;
  };
}

document.addEventListener("alpine:init", () => {
  Alpine.data("signature", () => {
    return {
      CW: 500,
      CH: 300,
      CanvW: 500,
      CanvH: 300,
      W: 0,
      H: 0,
      left: 0,
      landscape: true,
      canvasMaxHeight: false,
      canvas: null,
      emptyCanv: false,

      hwCtl: new HandWritingCtl(),

      init() {
        this.hwCtl.initCanvas(this.$refs.canvas);

        window.addEventListener("resize", () => this.resize());
        window.addEventListener("orientationchange", () => this.resize());

        this.resize();
        setTimeout(() => this.resizeCanvas(), 100);
      },

      resize() {
        const mainC = this.$refs.mainContainer;
        const exBox = this.$refs.exampleBox;
        const title = this.$refs.title;

        this.W = mainC.offsetWidth;
        this.H = mainC.offsetHeight;
        this.landscape = this.W > this.H;

        this.left = Math.max(exBox.offsetWidth + 20, title.offsetWidth + 10);

        this.resizeCanvas();
        setTimeout(() => this.resizeCanvas(), 100);
      },

      async resizeCanvas() {
        const canvasBox = this.$refs.canvasBox;
        const W = canvasBox.offsetWidth;
        const H = canvasBox.offsetHeight;
        const RH = (W * this.CH) / this.CW;

        this.canvasMaxHeight = this.landscape && RH > H;

        if (this.canvasMaxHeight) {
          this.CanvH = H;
          this.CanvW = (H * this.CW) / this.CH;
        } else {
          this.CanvH = RH;
          this.CanvW = W;
        }

        this.hwCtl.setSize(this.CanvW, this.CanvH);
      },

      clear() {
        this.hwCtl.clear();
      },

      capture() {
        this.emptyCanv = false;
        if (this.hwCtl.empty()) {
          setTimeout(() => {
            this.emptyCanv = true;
          }, 300);
          return;
        }
        const data = this.hwCtl.capture();
        document.getElementById("id_img").value = data;
        document.getElementById("form1").submit();
      },
    };
  });
});
