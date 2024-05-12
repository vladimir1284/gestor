// @ts-check
/** @type {import('alpinejs').default} */
var Alpine;

/**
 * @returns {{name: string, value: string}}
 * */
function getToken() {
  const input = /** @type {HTMLInputElement}*/ (
    document.querySelector("#csrf_token input")
  );
  const name = input.name;
  const value = input.value;
  return { name, value };
}

/**
 * @returns {Promise<Map<string, string>>}
 * */
async function getOptions() {
  const resp = await fetch(window.tv_options_url);
  if (resp.status != 200) {
    console.error({
      status: resp.status,
      statusText: resp.statusText,
      text: await resp.text(),
    });
  }
  const data = await resp.json();
  return data;
}

/**
 * @param {Map<string, string>} options
 * @returns {Promise<Map<string, string>>}
 * */
async function saveOptions(options) {
  const csrf = getToken();
  const opts = Object.fromEntries(options);

  const body = new FormData();
  body.set(csrf.name, csrf.value);
  body.set("data", JSON.stringify(opts));

  const resp = await fetch(window.tv_options_url, {
    method: "POST",
    body: body,
  });

  if (resp.status != 200) {
    console.error({
      status: resp.status,
      statusText: resp.statusText,
      text: await resp.text(),
    });
  }
  const data = await resp.json();
  return data;
}

/** @typedef {{option: string, value: string}} Option */
/** @typedef {Array<Option>} Options */

/**
 * @param {Map<string, string> | null} map
 * @returns {Options}
 * */
function fromMap(map) {
  if (!map) {
    return [];
  }
  /** @type {Options}*/
  const opts = [];
  for (let k in map) {
    opts.push({
      option: k,
      value: map[k],
    });
  }
  return opts;
}

/**
 * @param {Options} opt
 * @returns {Map<string, string>}
 * */
function toMap(opt) {
  /** @type {Map<string, string>}*/
  const map = new Map();
  for (let o of opt) {
    map.set(o.option, o.value);
  }
  return map;
}

document.addEventListener("alpine:init", () => {
  Alpine.data("templateVersionOptions", () => {
    return {
      loading: false,
      /** @type {Options} */
      options: [],
      selected: -1,
      value: false,
      toRemove: -1,

      init() {
        this.load();
      },

      async load() {
        this.loading = true;
        try {
          const data = await getOptions();
          this.options = fromMap(data);
        } catch (e) {
          console.log(e);
        }
        this.loading = false;
      },

      async save() {
        this.loading = true;
        if (this.options == null) return;
        try {
          const map = toMap(this.options);
          const data = await saveOptions(map);
          this.options = fromMap(data);
        } catch (e) {
          console.log(e);
        }
        this.loading = false;
      },

      add() {
        this.options.push({
          option: "Option",
          value: "Value",
        });
      },

      /**
       * @param {number} idx
       * */
      editOption(idx) {
        this.selected = idx;
        this.value = false;
      },

      /**
       * @param {number} idx
       * */
      editValue(idx) {
        this.selected = idx;
        this.value = true;
      },

      unselect() {
        this.selected = -1;
      },

      /**
       * @param {number} idx
       * */
      remove(idx) {
        this.options.splice(idx, 1);
      },

      /**
       * @param {number}idx
       * @param {boolean} val
       * @returns {boolean}
       * */
      isActive(idx, val) {
        return this.selected == idx && val == this.value;
      },
    };
  });
});
