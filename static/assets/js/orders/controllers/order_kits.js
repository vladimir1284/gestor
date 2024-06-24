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
        /** @type {{shortcut: string[], description: string}[]} */
        shortcutHelper: [],

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
        /** @type {boolean} */
        searchKitInputFocus: false,

        /** @type {string} */
        shortcut: "Alt+K",
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
          });

          const closeThis = () => {
            this.closeNewKitMode();
          };
          if (globalThis["closeAll"]) {
            globalThis["closeAll"].push(closeThis);
          } else {
            globalThis["closeAll"] = [closeThis];
          }

          // Shortcuts
          /** @type {{shortcut: string | string[], func: function, description: string, direct?: boolean}[]} */
          const shortcuts = [
            {
              shortcut: this.shortcut,
              description: "Open the dialog to add new kit",
              func: () => {
                this.closeAll();
                this.openNewKitMode();
              },
              direct: true,
            },
            {
              shortcut: "Alt+H",
              description: "Open this dialog with shortcuts",
              func: () => {
                this.$refs.shortcutButton.dispatchEvent(new Event("click"));
              },
            },
            {
              shortcut: "Escape",
              description: "Close the dialogs",
              func: () => this.closeNewKitMode(),
            },
            {
              shortcut: "Enter",
              description: "Add the selected kit",
              func: () => this.addKit(),
            },
            {
              shortcut: "Alt+Space",
              description: "Focus the search bar",
              func: () => this.focusSearch(),
            },
            {
              shortcut: "Alt+Shift+Space",
              description:
                "Focus the search bar and select the text in the bar",
              func: () => this.focusSearch(true),
            },
            {
              shortcut: ["Alt+ArrowUp", "ArrowUp"],
              description: "Select the previous kit on the list",
              func: () => this.selectPreviousItem(),
            },
            {
              shortcut: ["Alt+ArrowDown", "ArrowDown"],
              description: "Select the next kit on the list",
              func: () => this.selectNextItem(),
            },
          ];
          this.initShortcuts(shortcuts);
        },

        // Shortcuts methods

        /**
         * Create a shortcut function that run if the dialog is active
         * @param {string | string[]} shortcut - the function to execute
         * @param {Function} callback - the function to execute
         * */
        createShortcut(shortcut, callback) {
          globalThis.bindShortcut(shortcut, (/**@type {KeyboardEvent}*/ e) => {
            if (!this.newKitMode()) {
              return;
            }
            e.preventDefault();
            callback();
          });
        },

        /**
         * Init the shortcuts
         * @param {{shortcut: string | string[], func: function, description: string, direct?: boolean}[]} shortcuts
         * */
        initShortcuts(shortcuts) {
          for (let sc of shortcuts) {
            if (sc.direct) {
              globalThis.bindShortcut(sc.shortcut, () => sc.func());
            } else {
              this.createShortcut(sc.shortcut, sc.func);
            }
            let shortcut = sc.shortcut;
            if (!(shortcut instanceof Array)) {
              shortcut = [shortcut];
            }
            this.shortcutHelper.push({
              shortcut,
              description: sc.description,
            });
          }
        },

        // focus tools

        /**
         * Focus search input
         * @param {boolean} [select] - Specify if select the current text
         * */
        focusSearch(select) {
          const input = /**@type {HTMLInputElement}*/ (this.$refs.searchKit);
          input.focus();
          if (select) {
            input.select();
          }
        },

        // Selector tools

        /**
         * Select next item
         * */
        selectNextItem() {
          this.newKitIndex++;
          if (this.newKitIndex >= this.filteredKits.length) {
            this.newKitIndex = this.filteredKits.length - 1;
          }
        },

        /**
         * Select next item
         * */
        selectPreviousItem() {
          this.newKitIndex--;
          if (this.newKitIndex < 0) {
            this.newKitIndex = 0;
          }
        },

        /**
         * @returns {Kit | null}
         * */
        selectedKit() {
          if (this.filteredKits.length == 0) {
            return null;
          }
          return this.filteredKits[this.newKitIndex];
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
          this.newKitIndex = 0;
        },

        /**
         * Add the selected kit to the order
         * @param {Kit | null} [addKit]
         * */
        async addKit(addKit) {
          if (!addKit) {
            addKit = this.selectedKit();
          }
          if (addKit == null) {
            return;
          }

          addKit.loading = true;
          this.creating = true;

          try {
            /**@type {KitCreation}*/
            const kit = {
              id: addKit.id,
              tax: true,
              quantity: 1,
              price: addKit.suggested_price,
            };
            await kitApiClient.addKit(globalThis.OrderID, kit);
            this.reloadTransactions();
            this.loadKits();
          } catch (e) {
            console.log(e);
            globalThis.showNotify({
              title: "Error",
              msg: `Fail to create the new ${this.transactionType}`,
              status: "danger",
            });
          }

          this.closeNewKitMode();
          addKit.loading = false;
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
          let filtered = this.kits.filter((k) => {
            const st = globalThis.advanceMatch(k.name, this.newKitSearch);
            k.searchType = st;
            return st !== undefined && st !== -1;
          });

          filtered = filtered.sort((a, b) => {
            if (b.searchType === undefined || b.searchType === -1) {
              return -1;
            }
            if (a.searchType === undefined || a.searchType === -1) {
              return 1;
            }
            return a.searchType - b.searchType;
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
