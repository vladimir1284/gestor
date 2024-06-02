// @ts-check

/** @typedef {import('../models/product.js').Product} */

/**
 * Obtains the products list (type = parts)
 * @returns {Promise<Array<Product>>}
 * */
globalThis.getPartProducts = async function () {
  const resp = await fetch(globalThis.OrderPartsProductsUrl);
  if (resp.status != 200) {
    throw resp;
  }
  const data = await resp.json();
  return data;
};
