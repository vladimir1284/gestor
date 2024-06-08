// @ts-check

/** @typedef {import('../models/product.js').Product} */

class _ProductApiClient {
  /**
   * @param {string} baseUrl
   * */
  constructor(baseUrl) {
    this.BaseUrl = baseUrl;
  }

  /**
   * @returns {Promise<Array<Product>>}
   * */
  async getProducts() {
    const resp = await fetch(this.BaseUrl);
    if (resp.status != 200) {
      throw resp;
    }
    const data = await resp.json();
    return data;
  }
}

globalThis.ProductApiClient = _ProductApiClient;
