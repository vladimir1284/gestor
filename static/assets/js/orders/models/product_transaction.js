// @ts-check

/** @typedef {import('./unit.js').Unit} */
/** @typedef {import('./product.js').Product} */

/**
 * @typedef ProductTransaction
 * @property {number?} id
 * @property {Product} product
 * @property {Unit} unit
 * @property {number} cost
 * @property {boolean} done
 * @property {boolean | null} decline
 * @property {boolean} satisfied
 * @property {number} tax
 * @property {number} price
 * @property {number} quantity
 * @property {boolean} active_tax
 * @global
 * */

/**
 * @typedef ProductTransactionCreation
 * @property {number} product_id
 * @property {number} tax
 * @property {number} price
 * @property {number} quantity
 * @property {boolean} active_tax
 * @global
 * */
