// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

(function () {
  /** @typedef {import('../models/kits.js').Kit} */
  /** @typedef {import('../models/kits.js').KitCreation} */

  document.addEventListener("alpine:init", () => {
    Alpine.data("OrderKits", () => {
      /** @type{globalThis.KitApiClient} */
      const kitApiClient = new globalThis.KitApiClient(globalThis.KitUrl);

      return {
        // Controller properties

        /** @type {boolean} */
        loadingKit: false,
        /** @type {Array<Kit>} */
        kits: [],
        /** @type {string} */
        newKitSearch: "",
        /** @type {number} */
        newKitQty: 1,
        /** @type {number} */
        newKitPrice: 1,
        /** @type {boolean} */
        newKitTax: false,
        /** @type {boolean} */
        searchKitInputFocus: false,

        /** @type {Kit | null} */
        selectedKit: null,

        /** @type {string} */
        shortcut: "alt+k",
        /** @type {string} */
        transactionType: "kit",

        /** @type {boolean} */
        creating: false,

        // Initialization
        init() {
          this.loadKits();

          globalThis.bindShortcut(this.shortcut, () => {
            this.closeAll();
            this.openNewKitMode();
          });
          globalThis.bindShortcut("escape", () => {
            this.closeNewKitMode();
          });

          const closeThis = () => {
            this.closeNewKitMode();
          };
          if (globalThis["closeAll"]) {
            globalThis["closeAll"].push(closeThis);
          } else {
            globalThis["closeAll"] = [closeThis];
          }
        },

        /**
         * Close all others instances
         * */
        closeAll() {
          if (!globalThis["closeAll"]) return;

          for (let close of globalThis["closeAll"]) {
            if (close) close();
          }
        },

        // Dialog methods
        /**
         * Return true if we are in NewKitMode (If the kits dialog should be open)
         * @returns {boolean}
         * */
        newKitMode() {
          return this.searchKitInputFocus;
        },

        /**
         * Open the kits dialog and focus the search input
         * */
        openNewKitMode() {
          this.searchKitInputFocus = true;
          this.$refs.searchKit.focus();
          setTimeout(() => {
            this.$refs.searchKit.focus();
          }, 500);
        },

        /**
         * Close the kits dialog and reset the search value
         * */
        closeNewKitMode() {
          this.searchKitInputFocus = false;
          this.newKitSearch = "";
          this.unselectKit();
        },

        /**
         * Return if the user select a kit to add
         * */
        selectedKitMode() {
          return this.selectedKit != null;
        },

        /**
         * Set a selected kit
         * @param {Kit} kit
         * */
        selectKit(kit) {
          console.log(kit);
          this.selectedKit = kit;
          this.newKitPrice = kit.suggested_price;
          this.newKitQty = 1;
          this.newKitTax = true;
        },

        /**
         * Unselected the selected kit
         * */
        unselectKit() {
          this.selectedKit = null;
        },

        /**
         * Add the selected kit to the order
         * */
        async addKit() {
          if (!this.selectedKit) {
            return;
          }

          this.creating = true;

          try {
            /**@type {KitCreation}*/
            const kit = {
              id: this.selectedKit.id,
              tax: this.newKitTax,
              quantity: this.newKitQty,
              price: this.newKitPrice,
            };
            console.log(kit);
            await kitApiClient.addKit(globalThis.OrderID, kit);
            this.reloadTransactions();
          } catch (e) {
            console.log(e);
            globalThis.showNotify({
              title: "Error",
              msg: `Fail to create the new ${this.transactionType}`,
              status: "danger",
            });
          }

          this.unselectKit();
          this.closeNewKitMode();
          this.creating = false;
        },

        // Load Services
        async loadKits() {
          this.loadingKit = true;
          try {
            this.kits = await kitApiClient.getKitList(globalThis.OrderID);
          } catch (e) {
            console.error(e);
            globalThis.showNotify({
              title: "Error",
              msg: `Fail to load available ${this.transactionType} list`,
              status: "danger",
            });
          }
          this.loadingKit = false;
        },

        reloadTransactions() {
          const transTypes = [
            "reload_part",
            "reload_consumable",
            "reload_service",
          ];

          for (let tt of transTypes) {
            if (globalThis[tt]) {
              globalThis[tt]();
            }
          }
        },
      };
    });
  });
})();
