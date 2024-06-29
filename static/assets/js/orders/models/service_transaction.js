// @ts-check

/** @typedef {import('./service.js').Service} */

/**
 * @typedef ServiceTransaction
 * @property {number} id
 * @property {Service} service
 * @property {number} tax
 * @property {number} price
 * @property {number} quantity
 * @property {boolean} [loading]
 * @property {boolean} [select_for_kit]
 * */

/**
 * @typedef ServiceTransactionCreation
 * @property {number} service_id
 * @property {number} tax
 * @property {number} price
 * @property {number} quantity
 * */
