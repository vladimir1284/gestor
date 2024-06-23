// @ts-check

/** @typedef {import('./kits_elements.js').KitElement} */
/** @typedef {import('./kits_services.js').KitService} */

/**
 * @typedef Kit
 * @property {number} id
 * @property {string} name
 * @property {boolean} available
 * @property {number} min_price
 * @property {number} suggested_price
 * @property {KitElement[]} elements
 * @property {KitService[]} services
 * @property {boolean} [loading]
 * @property {number} [searchType]
 * */

/**
 * @typedef KitCreation
 * @property {number} id
 * @property {number} quantity
 * @property {number} price
 * @property {boolean} tax
 * */
