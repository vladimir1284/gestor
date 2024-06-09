// @ts-check

(function () {
  /** @typedef {import('../models/service.js').Service} */

  class _ServiceApiClient {
    /**
     * @param {string} baseUrl
     * */
    constructor(baseUrl) {
      this.BaseUrl = baseUrl;
    }

    /**
     * @returns {Promise<Array<Service>>}
     * */
    async getServices() {
      const resp = await fetch(this.BaseUrl);
      if (resp.status != 200) {
        throw resp;
      }
      const data = await resp.json();
      return data;
    }
  }

  globalThis.ServiceApiClient = _ServiceApiClient;
})();
