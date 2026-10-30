"use strict";
/* Truss analysis web client.
 *
 * Modules (plain objects, no build step):
 *   Api       - fetch wrapper for the gateway
 *   Renderer  - draws a scene description (SVG); reports clicks on clickable items
 *   Editor    - the five input tables
 *   App       - state + wiring; enforces "one joint/member at a time"
 */

const SVG_NS = "http://www.w3.org/2000/svg";
const SUPPORT_KINDS = ["pin", "roller_y", "roller_x"];

const Api = {
  async request(method, url, body) {
    const res = await fetch(url, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(data.detail || res.statusText);
      err.status = res.status;
      throw err;
    }
    return data;
  },
  get: (url) => Api.request("GET", url),
  post: (url, body) => Api.request("POST", url, body),
  put: (url, body) => Api.request("PUT", url, body),
};

/* ---------------------------------------------------------------- Renderer */
class Renderer {
  constructor(svg, onSelect) {
    this.svg = svg;
    this.onSelect = onSelect;
    this.scene = null;
    svg.addEventListener("click", (event) => {
      const target = event.target.closest("[data-kind]");
      if (target && this.onSelect) this.onSelect(target.dataset.kind, target.dataset.id);
    });
    new ResizeObserver(() => this.draw()).observe(svg);
  }

  show(scene) { this.scene = scene; this.draw(); }

  el(name, attrs = {}, parent = this.svg) {
    const node = document.createElementNS(SVG_NS, name);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    parent.appendChild(node);
    return node;
  }

  draw() {
    const svg = this.svg;
    svg.replaceChildren();
    if (!this.scene) return;
    const W = svg.clientWidth || 800, H = svg.clientHeight || 500;
    const [xmin, ymin, xmax, ymax] = this.scene.bounds;
    const overview = this.scene.mode === "overview";
    const padX = overview ? 95 : 150, padY = overview ? 70 : 80;  // room for the labels
    const scale = Math.max(1e-9, Math.min((W - 2 * padX) / (xmax - xmin), (H - 2 * padY) / (ymax - ymin)));
    const ox = (W - (xmax - xmin) * scale) / 2, oy = (H - (ymax - ymin) * scale) / 2;
    const sx = (x) => ox + (x - xmin) * scale;
    const sy = (y) => H - (oy + (y - ymin) * scale);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    for (const item of this.scene.items) this["draw_" + item.type](item, sx, sy);
  }

  mark(node, ref) {
    if (!ref) return node;
    node.dataset.kind = ref.kind;
    node.dataset.id = ref.id;
    return node;
  }

  draw_line(l, sx, sy) {
    const attrs = { x1: sx(l.x1), y1: sy(l.y1), x2: sx(l.x2), y2: sy(l.y2),
      "stroke-width": l.width, "stroke-linecap": "round", class: "r-" + l.role };
    if (l.dash) attrs["stroke-dasharray"] = "6 5";
    this.el("line", attrs);
    if (l.ref) {  // wide invisible line: easy to click on a thin member
      this.mark(this.el("line", { ...attrs, class: "hit", "stroke-width": l.width + 14 }), l.ref);
    }
  }

  draw_polygon(p, sx, sy) {
    const points = p.points.map(([x, y]) => `${sx(x)},${sy(y)}`).join(" ");
    this.el("polygon", { points, "stroke-width": p.width, class: "r-" + p.role + (p.fill ? " filled" : ""),
      fill: p.fill ? "" : "none", "stroke-linejoin": "round" });
  }

  draw_arrow(a, sx, sy) {
    const x1 = sx(a.x1), y1 = sy(a.y1), x2 = sx(a.x2), y2 = sy(a.y2);
    const len = Math.hypot(x2 - x1, y2 - y1) || 1;
    const ux = (x2 - x1) / len, uy = (y2 - y1) / len;
    const head = Math.min(13, len * 0.5), half = head * 0.42;
    const bx = x2 - ux * head, by = y2 - uy * head;
    this.el("line", { x1, y1, x2: bx, y2: by, "stroke-width": a.width, "stroke-linecap": "round",
      class: "r-" + a.role });
    const role = a.role.replace("force_", "");
    this.el("polygon", { points: `${x2},${y2} ${bx - uy * half},${by + ux * half} ${bx + uy * half},${by - ux * half}`,
      class: "head-" + role, stroke: "none" });
  }

  draw_dot(d, sx, sy) {
    const node = this.el("circle", { cx: sx(d.x), cy: sy(d.y), r: d.radius, class: "r-" + d.role + (d.ref ? " clickable" : "") });
    this.mark(node, d.ref);
  }

  draw_label(l, sx, sy) {
    const node = this.el("text", { x: sx(l.x) + l.dx, y: sy(l.y) + l.dy, "text-anchor": l.anchor,
      "font-size": l.size, "font-weight": l.bold ? 700 : 400, class: "t-" + l.role });
    node.textContent = l.text;
  }
}

/* ------------------------------------------------------------------ Editor */
const TABLES = {
  points: { prefix: "P", cols: [["id", "text"], ["name", "text"], ["x", "number"], ["y", "number"]] },
  members: { prefix: "T", cols: [["id", "text"], ["name", "text"], ["start_point", "points"],
    ["end_point", "points"], ["material", "materials"]] },
  materials: { prefix: "M", cols: [["id", "text"], ["name", "text"], ["A", "number"], ["E", "number"],
    ["density", "number"]] },
  loads: { prefix: "L", cols: [["id", "text"], ["name", "text"], ["point", "points"], ["Fx", "number"],
    ["Fy", "number"]] },
  supports: { prefix: "S", cols: [["id", "text"], ["name", "text"], ["point", "points"], ["type", "kinds"]] },
};

class Editor {
  constructor(root, tabs, app) {
    this.root = root; this.tabs = tabs; this.app = app; this.active = "points";
  }

  render() {
    const { app } = this, t = (key, params) => app.t(key, params);
    this.tabs.replaceChildren();
    for (const name of Object.keys(TABLES)) {
      const b = document.createElement("button");
      b.type = "button"; b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(name === this.active));
      b.textContent = t("tab." + name);
      b.onclick = () => { this.active = name; this.render(); };
      this.tabs.appendChild(b);
    }
    const spec = TABLES[this.active], rows = app.truss[this.active] || [];
    const table = document.createElement("table");
    const head = table.createTHead().insertRow();
    for (const [key] of spec.cols) head.insertCell().outerHTML = `<th>${t("col." + key)}</th>`;
    head.insertCell();
    const body = table.createTBody();
    rows.forEach((row, index) => {
      const tr = body.insertRow();
      for (const [key, type] of spec.cols) tr.insertCell().appendChild(this.input(row, key, type, index));
      const del = document.createElement("button");
      del.type = "button"; del.textContent = "✕"; del.title = t("ui.delete");
      del.onclick = () => { rows.splice(index, 1); this.render(); app.modelChanged(); };
      tr.insertCell().appendChild(del);
    });
    const add = document.createElement("button");
    add.type = "button"; add.className = "add"; add.textContent = t("ui.add_row");
    add.onclick = () => { rows.push(this.blankRow(this.active)); app.truss[this.active] = rows; this.render(); app.modelChanged(); };
    this.root.replaceChildren(table, add);
  }

  options(type) {
    const truss = this.app.truss;
    if (type === "points") return (truss.points || []).map((p) => [p.id, p.id]);
    if (type === "materials") return (truss.materials || []).map((m) => [m.id, m.id]);
    return SUPPORT_KINDS.map((k) => [k, this.app.t("support." + k)]);
  }

  input(row, key, type, index) {
    let node;
    if (type === "text" || type === "number") {
      node = document.createElement("input");
      node.type = type === "number" ? "number" : "text";
      if (type === "number") node.step = "any";
      node.value = row[key] ?? "";
    } else {
      node = document.createElement("select");
      const opts = this.options(type);
      if (!opts.some(([v]) => v === row[key])) opts.unshift([row[key] ?? "", row[key] || "—"]);
      for (const [value, label] of opts) node.add(new Option(label, value, false, value === row[key]));
    }
    node.setAttribute("aria-label", key + " " + (index + 1));
    node.onchange = () => {
      row[key] = type === "number" ? (node.value === "" ? null : Number(node.value)) : node.value;
      if (key === "id") this.render();
      this.app.modelChanged();
    };
    return node;
  }

  blankRow(name) {
    const rows = this.app.truss[name], prefix = TABLES[name].prefix;
    let n = rows.length + 1;
    while (rows.some((r) => r.id === prefix + n)) n++;
    const id = prefix + n;
    const points = this.app.truss.points || [];
    const first = points.length ? points[0].id : "";
    const mats = this.app.truss.materials || [];
    switch (name) {
      case "points": return { id, name: id, x: 0, y: 0 };
      case "members": return { id, name: id, start_point: first, end_point: first, material: mats.length ? mats[0].id : "" };
      case "materials": return { id, name: id, A: 0.001, E: 200, density: 7850 };
      case "loads": return { id, name: id, point: first, Fx: 0, Fy: 0 };
      default: return { id, name: id, point: first, type: "pin" };
    }
  }
}

/* --------------------------------------------------------------------- App */
const App = {
  id: null, truss: {}, lang: localStorage.getItem("lang") || "en", i18n: {}, mode: "overview",
  target: null, view: null, timer: null, seq: 0,

  t(key, params = {}) {
    let text = this.i18n[key] ?? key;
    for (const [k, v] of Object.entries(params)) text = text.replaceAll(`{${k}}`, v);
    return text;
  },

  $(id) { return document.getElementById(id); },

  async init() {
    this.renderer = new Renderer(this.$("canvas"), (kind, id) => this.select(kind, id));
    this.editor = new Editor(this.$("editor-body"), this.$("tabs"), this);
    const languages = await Api.get("/api/languages");
    const select = this.$("language");
    for (const [code, name] of Object.entries(languages)) select.add(new Option(name, code, false, code === this.lang));
    select.onchange = async () => { this.lang = select.value; localStorage.setItem("lang", this.lang); await this.loadI18n(); this.refreshAll(); };
    this.$("btn-back").onclick = () => this.back();
    this.$("btn-load-template").onclick = () => this.loadTemplate(this.$("template").value);
    this.$("btn-save").onclick = () => this.saveFile();
    this.$("btn-open").onclick = () => this.$("file-input").click();
    this.$("file-input").onchange = (e) => this.openFile(e.target.files[0]);
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && this.mode !== "overview") this.back(); });
    await this.loadI18n();
    this.templates = await Api.get("/api/templates");
    this.fillTemplates();
    await this.loadTemplate(this.templates[0].key);
  },

  async loadI18n() {
    this.i18n = await Api.get(`/api/i18n/${this.lang}`);
    document.documentElement.lang = this.lang;
    this.fillStaticTexts();
  },

  fillStaticTexts() {
    const set = (id, key) => { this.$(id).textContent = this.t(key); };
    set("app-title", "app.title"); set("app-caption", "app.caption"); set("lbl-language", "ui.language");
    set("lbl-template", "ui.template"); set("btn-load-template", "ui.load_template");
    set("btn-open", "ui.open"); set("btn-save", "ui.save"); set("btn-back", "ui.back");
    document.title = this.t("app.title");
    if (this.templates) { const keep = this.$("template").value; this.fillTemplates(); this.$("template").value = keep; }
    this.$("legend").innerHTML = ["tension", "compression", "zero"].map(
      (s) => `<li><i style="background:var(--${s})"></i>${this.t("ui.legend_" + s)}</li>`).join("");
  },

  fillTemplates() {
    const select = this.$("template");
    select.replaceChildren();
    for (const tpl of this.templates) {
      const label = this.i18n["template." + tpl.key] || tpl.name;
      select.add(new Option(label, tpl.key));
    }
  },

  async loadTemplate(key) {
    const created = await Api.post("/api/trusses", { template: key });
    this.id = created.id; this.truss = created.truss;
    this.mode = "overview"; this.target = null;
    this.editor.render();
    await this.fetchView();
  },

  /* ---- selection: one joint OR one member at a time ---- */
  select(kind, id) {
    if (this.mode !== "overview") return;  // go back first
    this.mode = kind; this.target = id;
    this.fetchView();
  },

  back() { this.mode = "overview"; this.target = null; this.fetchView(); },

  /* ---- model edits: debounce, save, redraw ---- */
  modelChanged() {
    clearTimeout(this.timer);
    this.timer = setTimeout(async () => {
      try { await Api.put(`/api/trusses/${this.id}`, this.truss); }
      catch (e) { this.showError(e); return; }
      this.mode = "overview"; this.target = null;
      await this.fetchView();
    }, 350);
  },

  async fetchView() {
    const ticket = ++this.seq;
    const qs = new URLSearchParams({ mode: this.mode, target: this.target || "", lang: this.lang });
    if (!this.target) qs.delete("target");
    try {
      const view = await Api.get(`/api/trusses/${this.id}/view?${qs}`);
      if (ticket !== this.seq) return;  // a newer request superseded this one
      this.view = view;
      this.renderView();
    } catch (e) {
      if (e.status === 409 || e.status === 404) { this.mode = "overview"; this.target = null; return this.fetchView(); }
      this.showError(e);
    }
  },

  renderView() {
    const v = this.view;
    this.renderer.show(v.scene);
    this.$("stage-title").textContent = v.scene.title;
    const name = v.scene.title.replace(/^[^ ]+ /, "");
    this.$("stage-hint").textContent = v.mode === "overview" ? this.t("ui.hint_overview")
      : this.t(v.mode === "joint" ? "ui.hint_joint" : "ui.hint_member", { name });
    this.$("btn-back").hidden = v.mode === "overview";
    this.$("legend").hidden = !(v.status === "solved");
    const status = this.$("status");
    status.className = "status " + v.status;
    status.textContent = v.status_text;
    this.$("issues").replaceChildren(...v.issues.map((text) => Object.assign(document.createElement("li"), { textContent: text })));
    this.renderTables(v.panels);
  },

  renderTables(panels) {
    const root = this.$("tables");
    root.replaceChildren();
    for (const p of panels) {
      const h = document.createElement("h3"); h.textContent = p.title;
      const table = document.createElement("table");
      const hasHead = p.columns.some((c) => c !== "");
      if (hasHead) {
        const tr = table.createTHead().insertRow();
        for (const c of p.columns) tr.insertCell().outerHTML = `<th>${c}</th>`;
      }
      const body = table.createTBody();
      for (const row of p.rows) {
        const tr = body.insertRow();
        for (const cell of row) tr.insertCell().textContent = cell;
      }
      root.append(h, table);
      if (p.note) {
        const note = document.createElement("div");
        note.className = "note " + (p.note_ok ? "ok" : "bad");
        note.textContent = p.note;
        root.append(note);
      }
    }
  },

  showError(e) {
    const status = this.$("status");
    status.className = "status invalid_input";
    status.textContent = `${this.t("ui.error")}: ${e.message}`;
  },

  refreshAll() { this.editor.render(); this.fetchView(); },

  saveFile() {
    const blob = new Blob([JSON.stringify(this.truss, null, 2)], { type: "application/json" });
    const link = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: "truss.json" });
    link.click();
    URL.revokeObjectURL(link.href);
  },

  async openFile(file) {
    if (!file) return;
    try {
      const created = await Api.post("/api/trusses", { truss: JSON.parse(await file.text()) });
      this.id = created.id; this.truss = created.truss; this.mode = "overview"; this.target = null;
      this.editor.render(); await this.fetchView();
    } catch (e) { this.showError(e); }
    this.$("file-input").value = "";
  },
};

App.init().catch((e) => App.showError(e));
