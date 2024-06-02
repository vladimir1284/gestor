// @ts-check

/** @typedef {import('../models/product_transaction.js').ProductTransaction} */
/** @typedef {import('../models/product_transaction.js').ProductTransactionCreation} */

/**
 * Get the API url
 * @param {number} order_id
 * @param {number?} trans_id
 * */
function getURL(order_id, trans_id = null) {
  if (trans_id) {
    return `${globalThis.OrderPartsUrl}/${order_id}/${trans_id}/`;
  }
  return `${globalThis.OrderPartsUrl}/${order_id}/`;
}

/**
 * Obtains the order parts
 * @param {number} order_id - The order ID
 * @returns {Promise<Array<ProductTransaction>>}
 * */
globalThis.getOrderParts = async function (order_id) {
  const resp = await fetch(getURL(order_id));
  if (resp.status != 200) {
    throw resp;
  }
  const data = await resp.json();
  return data;
};

/**
 * Add an order parts
 * @param {number} order_id - The order ID
 * @param {ProductTransactionCreation} trans - The part to add
 * */
globalThis.addOrderParts = async function (order_id, trans) {
  const csrftoken = globalThis.getCookie("csrftoken");
  const resp = await fetch(getURL(order_id), {
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
};

/**
 * Update an order parts
 * @param {number} order_id - The order ID
 * @param {number} trans_id - The part ID
 * @param {ProductTransactionCreation} trans - The part to update
 * */
globalThis.updateOrderParts = async function (order_id, trans_id, trans) {
  const csrftoken = globalThis.getCookie("csrftoken");
  const resp = await fetch(getURL(order_id, trans_id), {
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
};

/**
 * Remove an order parts
 * @param {number} order_id - The order ID
 * @param {number} trans_id - The transaction ID to remove
 * */
globalThis.removeOrderParts = async function (order_id, trans_id) {
  const csrftoken = globalThis.getCookie("csrftoken");
  const resp = await fetch(getURL(order_id, trans_id), {
    method: "DELETE",
    headers: { "X-CSRFToken": csrftoken ? csrftoken : "" },
    credentials: "same-origin",
  });
  if (resp.status != 200 && resp.status != 204) {
    throw resp;
  }
};
