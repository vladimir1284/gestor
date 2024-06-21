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
        /** @type {Array<Kit>} */
        filteredKits: [],
        /** @type {string} */
        newKitSearch: "",
        /** @type {number} */
        newKitIndex: 0,
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
          this.$watch("newKitSearch", () => {
            this.filteredKits = this.getFiltered();
          });
          this.loadKits();

          globalThis.bindShortcut(this.shortcut, () => {
            this.closeAll();
            this.openNewKitMode();
          });
          globalThis.bindShortcut("escape", () => {
            this.closeNewKitMode();
          });

          globalThis.bindShortcut(
            "alt+arrowup",
            (/**@type {KeyboardEvent}*/ e) => {
              if (!this.newKitMode()) {
                return;
              }
              e.preventDefault();
              this.newKitIndex--;
              if (this.newKitIndex < 0) {
                this.newKitIndex = this.filteredKits.length - 1;
              }
            },
          );
          globalThis.bindShortcut(
            "alt+arrowdown",
            (/**@type {KeyboardEvent}*/ e) => {
              if (!this.newKitMode()) {
                return;
              }
              e.preventDefault();
              this.newKitIndex++;
              if (this.newKitIndex >= this.filteredKits.length) {
                this.newKitIndex = 0;
              }
            },
          );

          globalThis.bindShortcut("enter", () => {
            if (!this.newKitMode()) {
              return;
            }
            if (!this.selectedKitMode()) {
              const kit = this.filteredKits[this.newKitIndex];
              if (kit.available) {
                this.selectKit(kit);
              }
            } else {
              this.addKit();
            }
          });
          globalThis.bindShortcut(
            "alt+arrowleft",
            (/**@type {KeyboardEvent}*/ e) => {
              if (!this.newKitMode() || !this.selectedKitMode()) {
                return;
              }
              e.preventDefault();
              this.selectedKit = null;
            },
          );
          globalThis.bindShortcut(
            "alt+arrowright",
            (/**@type {KeyboardEvent}*/ e) => {
              if (!this.newKitMode() || this.selectedKitMode()) {
                return;
              }
              e.preventDefault();
              const kit = this.filteredKits[this.newKitIndex];
              if (kit.available) {
                this.selectKit(kit);
              }
            },
          );
          globalThis.bindShortcut("alt+tab", (/**@type {KeyboardEvent}*/ e) => {
            if (!this.newKitMode() || !this.selectedKitMode()) {
              return;
            }
            e.preventDefault();
            this.switchEditableFocus();
          });
          globalThis.bindShortcut("alt+t", () => {
            if (!this.newKitMode() || !this.selectedKitMode()) {
              return;
            }
            this.newKitTax = !this.newKitTax;
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
          this.selectedKit = kit;
          this.newKitPrice = kit.suggested_price;
          this.newKitQty = 1;
          this.newKitTax = true;
          setTimeout(() => this.$refs.kitQty.focus(), 100);
        },

        switchEditableFocus() {
          if (document.activeElement === this.$refs.kitQty) {
            this.$refs.kitPrice.focus();
          } else {
            this.$refs.kitQty.focus();
          }
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
            this.filteredKits = this.getFiltered();
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

        // Get filter elements
        /**
         * @returns {Array<Kit>}
         * */
        getFiltered() {
          const filtered = this.kits.filter((k) => {
            return globalThis.match(k.name, this.newKitSearch);
          });

          this.newKitIndex = 0;
          return filtered;
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
