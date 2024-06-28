// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

function init() {
  if (globalThis._orderPSC) return;
  globalThis._orderPSC = true;

  /** @typedef {import('../models/product_transaction.js').ProductTransaction} */
  /** @typedef {import('../models/service_transaction.js').ServiceTransaction} */

  // Alpine.store("globalPSC", {});
  Alpine.data("OrderPSC", () => {
    return {
      psc: globalThis.globalPSC,
      kits: null,
      parts: null,
      services: null,
      consumables: null,

      init() {
        Alpine.effect(() => {
          this.kits = this.psc.kit;
        });
        Alpine.effect(() => {
          this.parts = this.psc.part;
        });
        Alpine.effect(() => {
          this.services = this.psc.service;
        });
        Alpine.effect(() => {
          this.consumables = this.psc.consumable;
        });
      },

      // Parts
      getParts() {
        if (!this.parts) {
          return [];
        }
        /** @type {Array<ProductTransaction>} */
        const transactions = this.parts.transactions;
        return transactions.sort((a, b) => {
          return (b.id ?? -1) - (a.id ?? -1);
        });
      },

      // Services
      getServices() {
        if (!this.services) {
          return [];
        }
        /** @type {Array<ServiceTransaction>} */
        const transactions = this.services.transactions;
        return transactions.sort((a, b) => {
          return (b.id ?? -1) - (a.id ?? -1);
        });
      },

      // Consumables
      getConsumables() {
        if (!this.consumables) {
          return [];
        }
        /** @type {Array<ProductTransaction>} */
        const transactions = this.consumables.transactions;
        return transactions.sort((a, b) => {
          return (b.id ?? -1) - (a.id ?? -1);
        });
      },
    };
  });
}

document.addEventListener("alpine:init", init);
