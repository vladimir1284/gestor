// @ts-check
/** @type {import('alpinejs').default} */
var Alpine;

/** @typedef {{option: string, value: string}} Option */
/** @typedef {Array<Option>} Options */

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
 * @returns {Promise<Options>}
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
 * @param {Options} options
 * @returns {Promise<Options>}
 * */
async function saveOptions(options) {
  const csrf = getToken();

  const jsonOpts = JSON.stringify(options);

  const body = new FormData();
  body.set(csrf.name, csrf.value);
  body.set("data", jsonOpts);

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
          this.options = await getOptions();
        } catch (e) {
          console.log(e);
        }
        this.loading = false;
      },

      async save() {
        this.loading = true;
        if (this.options == null) return;
        try {
          this.options = await saveOptions(this.options);
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
