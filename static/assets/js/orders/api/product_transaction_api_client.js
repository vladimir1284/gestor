// @ts-check

/** @typedef {import('../models/product_transaction.js').ProductTransaction} */
/** @typedef {import('../models/product_transaction.js').ProductTransactionCreation} */

class _ProductTransactionApiClient {
  /**
   * @param {string} baseUrl
   * */
  constructor(baseUrl) {
    this.BaseUrl = baseUrl;
  }

  /**
   * @param {number} order_id
   * @param {number} [trans_id]
   * */
  getURL(order_id, trans_id = undefined) {
    if (trans_id) {
      return `${this.BaseUrl}/${order_id}/${trans_id}/`;
    }
    return `${this.BaseUrl}/${order_id}/`;
  }

  /**
   * @param {number} order_id
   * @returns {Promise<Array<ProductTransaction>>}
   * */
  async getProductTransactionList(order_id) {
    const resp = await fetch(this.getURL(order_id));
    if (resp.status != 200) {
      throw resp;
    }
    const data = await resp.json();
    return data;
  }

  /**
   * @param {number} order_id
   * @param {ProductTransactionCreation} trans
   * */
  async addProductTransaction(order_id, trans) {
    const csrftoken = globalThis.getCookie("csrftoken");
    const resp = await fetch(this.getURL(order_id), {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken ? csrftoken : "",
        "content-type": "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify(trans),
    });
    if (resp.status != 200 && resp.status != 204) {
      throw resp;
    }
  }

  /**
   * @param {number} order_id
   * @param {number} trans_id
   * @param {ProductTransactionCreation} trans
   * */
  async updateProductTransaction(order_id, trans_id, trans) {
    const csrftoken = globalThis.getCookie("csrftoken");
    const resp = await fetch(this.getURL(order_id, trans_id), {
      method: "PUT",
      headers: {
        "X-CSRFToken": csrftoken ? csrftoken : "",
        "content-type": "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify(trans),
    });
    if (resp.status != 200 && resp.status != 204) {
      throw resp;
    }
  }

  /**
   * @param {number} order_id
   * @param {number} trans_id
   * */
  async removeProductTransaction(order_id, trans_id) {
    const csrftoken = globalThis.getCookie("csrftoken");
    const resp = await fetch(this.getURL(order_id, trans_id), {
      method: "DELETE",
      headers: { "X-CSRFToken": csrftoken ? csrftoken : "" },
      credentials: "same-origin",
    });
    if (resp.status != 200 && resp.status != 204) {
      throw resp;
    }
  }
}

globalThis.ProductTransactionApiClient = _ProductTransactionApiClient;
