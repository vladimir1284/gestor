// @ts-check

(function () {
  /** @typedef {import('../models/kits.js').Kit} */
  /** @typedef {import('../models/kits.js').KitCreation} */

  class _KitApiClient {
    /**
     * @param {string} baseUrl
     * */
    constructor(baseUrl) {
      this.BaseUrl = baseUrl;
    }

    /**
     * @param {number} order_id
     * @param {number} [kit_id]
     * */
    getURL(order_id, kit_id = undefined) {
      if (kit_id) {
        return `${this.BaseUrl}/${order_id}/${kit_id}/`;
      }
      return `${this.BaseUrl}/${order_id}/`;
    }

    /**
     * @param {number} order_id
     * @returns {Promise<Array<Kit>>}
     * */
    async getKitList(order_id) {
      const resp = await fetch(this.getURL(order_id));
      if (resp.status != 200) {
        throw resp;
      }
      const data = await resp.json();
      return data;
    }

    /**
     * @param {number} order_id
     * @param {Kit} kit
     * */
    async addKit(order_id, kit) {
      const csrftoken = globalThis.getCookie("csrftoken");
      const resp = await fetch(this.getURL(order_id), {
        method: "POST",
        headers: {
          "X-CSRFToken": csrftoken ? csrftoken : "",
          "content-type": "application/json",
        },
        credentials: "same-origin",
        body: JSON.stringify(kit),
      });
      if (resp.status != 200 && resp.status != 204) {
        throw resp;
      }
    }
  }

  globalThis.KitApiClient = _KitApiClient;
})();
