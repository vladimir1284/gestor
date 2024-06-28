// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

(function () {
  /** @typedef {import('../models/service_transaction.js').ServiceTransaction} */
  /** @typedef {import('../models/service_transaction.js').ServiceTransactionCreation} */
  /** @typedef {import('../models/service.js').Service} */

  const NONE = 0;
  const QTY = 1;
  const PRICE = 2;
  const TAX = 3;
  const EditMIN = NONE;
  const EditMAX = TAX;

  document.addEventListener("alpine:init", () => {
    Alpine.data("OrderService", () => {
      const serviceApiClient = new globalThis.ServiceApiClient(
        globalThis.ServiceUrl,
      );
      const serviceTransactionApiClient =
        new globalThis.ServiceTransactionApiClient(
          globalThis.ServiceTransactionUrl,
        );

      return {
        // Controller properties
        /** @type {{shortcut: string[], description: string[]}[]} */
        shortcutHelper: [],

        /** @type {boolean} */
        loadingServices: false,
        /** @type {Array<Service>} */
        services: [],
        /** @type {Array<Service>} */
        filteredServices: [],
        /** @type {string} */
        newServiceSearch: "",
        /** @type {number} */
        newServiceIndex: 0,
        /** @type {number} */
        newServiceEditing: NONE,
        /** @type {boolean} */
        searchServiceInputFocus: false,

        /** @type {boolean} */
        loading: false,

        /** @type {Array<number>} */
        transactionsServices: [],
        /** @type {Array<ServiceTransaction>} */
        transactions: [],
        transactions_args: {
          total: 0,
          amount: 0,
          tax: 0,
        },

        toRemove: -1,
        removing: false,

        shortcut: "alt+s",
        transactionType: "service",

        // Initialization
        init() {
          // this.$store.globalPSC[this.transactionType] = this;
          if (!globalThis.globalPSC) {
            globalThis.globalPSC = Alpine.reactive({});
          }
          globalThis.globalPSC[this.transactionType] = this;

          this.$watch("transactions", (transactions) => {
            this.transactions_args.total = 0;
            this.transactions_args.amount = 0;
            this.transactions_args.tax = 0;

            for (let transaction of transactions) {
              if (
                this.transactionsServices.indexOf(transaction.service.id) == -1
              ) {
                this.transactionsServices.push(transaction.service.id);
              }
              const amount = this.getAmount(transaction);
              const tax = this.getTax(transaction);
              const total = amount + tax;

              this.transactions_args.total += total;
              this.transactions_args.amount += amount;
              this.transactions_args.tax += tax;
            }

            this.filteredServices = this.getFiltered();
          });

          this.$watch("newServiceSearch", () => {
            this.filteredServices = this.getFiltered();
          });

          this.loadTransactions();
          this.loadServices();

          const closeThis = () => {
            this.closeNewServiceMode();
          };
          if (globalThis["closeAll"]) {
            globalThis["closeAll"].push(closeThis);
          } else {
            globalThis["closeAll"] = [closeThis];
          }

          globalThis[`reload_${this.transactionType}`] = () => {
            this.loadTransactions();
          };

          // Shortcuts
          /** @type {{shortcut: string | string[], func: function, description: string | string[], direct?: boolean}[]} */
          const shortcuts = [
            {
              shortcut: this.shortcut,
              description: [
                "Open the dialog to add new service",
                "Abrir el dialogo para agregar nuevos servicios",
              ],
              func: () => {
                this.closeAll();
                this.$refs.searchServices.focus();
              },
              direct: true,
            },
            {
              shortcut: "Alt+H",
              description: [
                "Open this dialog with shortcuts",
                "Abrir esta ventana con los atajos de teclado",
              ],
              func: () => {
                this.$refs.shortcutButton.dispatchEvent(new Event("click"));
              },
            },
            {
              shortcut: "Escape",
              description: ["Close the dialogs", "Cerrar los dialogos"],
              func: () => this.closeNewServiceMode(),
            },
            {
              shortcut: "Enter",
              description: [
                "Add the selected service",
                "Agregar el servicio seleccionado",
              ],
              func: () =>
                this.addNewTransaction(
                  this.filteredServices[this.newServiceIndex],
                ),
            },
            {
              shortcut: ["Alt+Space", "Alt+Enter"],
              description: [
                "Focus the search bar",
                "Enfocar la barra de busqueda",
              ],
              func: () => this.focusSearch(),
            },
            {
              shortcut: ["Alt+Shift+Space", "Alt+Shift+Enter"],
              description: [
                "Focus the search bar and select the text in the bar",
                "Enfocar la barra de busqueda y seleccionar el texto en la barra",
              ],
              func: () => this.focusSearch(true),
            },
            {
              shortcut: ["Alt+ArrowUp", "ArrowUp"],
              description: [
                "Select the previous service on the list",
                "Seleccionar el servicio anterior en la lista",
              ],
              func: () => this.selectPreviousItem(),
            },
            {
              shortcut: ["Alt+ArrowDown", "ArrowDown"],
              description: [
                "Select the next service on the list",
                "Seleccionar el servicio siguiente en la lista",
              ],
              func: () => this.selectNextItem(),
            },
            {
              shortcut: ["Tab", "Alt+Tab", "Alt+ArrowRight"],
              description: [
                "Focus the next editable (quantity, price and tax) on the selected service",
                "Enfocar el editable siguiente (cantidad, precio y impuesto) del servicio seleccionado",
              ],
              func: () => this.focusNextEditableOfSelected(),
            },
            {
              shortcut: ["Alt+ArrowLeft"],
              description: [
                "Focus the previous editable (quantity, price and tax) on the selected service",
                "Enfocar el editable anterior (cantidad, precio y impuesto) del servicio seleccionado",
              ],
              func: () => this.focusPreviousEditableOfSelected(),
            },
          ];
          this.initShortcuts(shortcuts);
        },

        // Tools

        /**
         * Scroll to element
         * @param {HTMLElement} el
         * */
        scrollTo(el) {
          setTimeout(() => {
            el.scrollIntoView({
              behavior: "smooth",
              block: "start",
              inline: "nearest",
            });
          }, 300);
        },

        /**
         * focus element
         * @param {HTMLElement} el
         * @param {boolean} [scroll]
         * */
        focusElement(el, scroll) {
          el.focus();
          if (scroll) this.scrollTo(el);
          if (el instanceof HTMLInputElement) {
            setTimeout(() => {
              el.select();
            }, 100);
          }
        },

        /**
         * focus element by id
         * @param {string} id
         * @param {boolean} [scroll]
         * */
        focusElementById(id, scroll) {
          const el = document.getElementById(id);
          if (el) this.focusElement(el, scroll);
        },

        // Shortcuts methods

        /**
         * Create a shortcut function that run if the dialog is active
         * @param {string | string[]} shortcut - the function to execute
         * @param {Function} callback - the function to execute
         * */
        createShortcut(shortcut, callback) {
          globalThis.bindShortcut(shortcut, (/**@type {KeyboardEvent}*/ e) => {
            if (!this.newServiceMode()) {
              return;
            }
            e.preventDefault();
            callback();
          });
        },

        /**
         * Init the shortcuts
         * @param {{shortcut: string | string[], func: function, description: string | string[], direct?: boolean}[]} shortcuts
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
            let description = sc.description;
            if (!(description instanceof Array)) {
              description = [description];
            }
            this.shortcutHelper.push({
              shortcut,
              description,
            });
          }
        },

        // focus tools

        /**
         * Focus search input
         * @param {boolean} [select] - Specify if select the current text
         * */
        focusSearch(select) {
          this.newServiceEditing = EditMIN;
          const input = /**@type {HTMLInputElement}*/ (
            this.$refs.searchServices
          );
          input.focus();
          if (select) {
            input.select();
          }
        },

        /**
         * Blur all editables elements
         * */
        blurEditables() {
          const editables = /**@type{NodeListOf<HTMLElement>}*/ (
            document.querySelectorAll(".service_editable.service_active")
          );

          for (let e of editables) {
            e.blur();
          }
        },

        /**
         * focus an editable element
         * @param {number} editable
         * */
        focusEditable(editable) {
          let type = "";
          switch (editable) {
            case QTY:
              type = "quantity";
              break;
            case PRICE:
              type = "price";
              break;
            case TAX:
              type = "tax";
              break;
          }
          if (type == "") return;
          const editableElement = /**@type{HTMLInputElement}*/ (
            document.querySelector(
              `.service_editable.service_active.service_selected.service_${type}`,
            )
          );
          if (!editableElement) return;
          this.focusElement(editableElement);
        },

        /**
         * focus an editable element blur others
         * @param {number} editable
         * */
        blurFocusEditable(editable) {
          this.blurEditables();
          this.focusEditable(editable);
        },

        /**
         * Focus next editable of selected element
         * */
        focusNextEditableOfSelected() {
          this.newServiceEditing++;
          if (this.newServiceEditing > EditMAX) {
            this.newServiceEditing = EditMIN;
          }
          this.blurFocusEditable(this.newServiceEditing);
        },

        /**
         * Focus previous editable of selected element
         * */
        focusPreviousEditableOfSelected() {
          this.newServiceEditing--;
          if (this.newServiceEditing < EditMIN) {
            this.newServiceEditing = EditMAX;
          }
          this.blurFocusEditable(this.newServiceEditing);
        },

        // Selector tools

        /**
         * Select next item
         * */
        selectNextItem() {
          this.newServiceIndex++;
          if (this.newServiceIndex >= this.filteredServices.length) {
            this.newServiceIndex = this.filteredServices.length - 1;
          }
          this.newServiceEditing = NONE;
          this.blurEditables();
        },

        /**
         * Select next item
         * */
        selectPreviousItem() {
          this.newServiceIndex--;
          if (this.newServiceIndex < 0) {
            this.newServiceIndex = 0;
          }
          this.newServiceEditing = NONE;
          this.blurEditables();
        },

        // Tools

        /**
         * @returns {string}
         * */
        titleTransactionType() {
          if (this.transactionType.length < 1) {
            return this.transactionType.toUpperCase();
          }
          return (
            this.transactionType.charAt(0).toUpperCase() +
            this.transactionType.substring(1).toLowerCase()
          );
        },

        // Load data
        async loadTransactions(loader = true) {
          if (loader) this.loading = true;
          try {
            this.transactions =
              await serviceTransactionApiClient.getServiceTransactionList(
                globalThis.OrderID,
              );
          } catch (e) {
            console.error(e);
            if (loader) {
              globalThis.showNotify({
                title: "Error",
                msg: `Fail to load order's ${this.transactionType} list`,
                status: "danger",
              });
            } else {
              globalThis.showNotify({
                title: "Error",
                msg: `Fail to reload order's ${this.transactionType} list`,
                status: "danger",
              });
            }
          }
          if (loader) this.loading = false;
        },

        // Load Services
        async loadServices() {
          this.loadingServices = true;
          try {
            this.services = await serviceApiClient.getServices();
            for (let service of this.services) {
              service.transaction_quantity = 1;
              service.transaction_price = service.suggested_price;
              service.transaction_tax = service.sell_tax;
            }
            this.filteredServices = this.getFiltered();
          } catch (e) {
            console.error(e);
            globalThis.showNotify({
              title: "Error",
              msg: `Fail to load available ${this.transactionType} list`,
              status: "danger",
            });
          }
          this.loadingServices = false;
        },

        /**
         * Render product, return true if should be rendered
         * @param {Service} service
         * @returns {boolean}
         * */
        renderService(service) {
          return this.transactionsServices.indexOf(service.id) == -1;
        },

        // Get filter elements
        /**
         * @returns {Array<Service>}
         * */
        getFiltered() {
          let filtered = this.services.filter((s) => {
            const st = globalThis.advanceMatch(s.name, this.newServiceSearch);
            s.searchType = st;
            return this.renderService(s) && st !== undefined && st !== -1;
          });

          filtered = filtered.sort((a, b) => {
            if (a.searchType == b.searchType) {
              return b.total_sells - a.total_sells;
            }
            if (b.searchType === undefined || b.searchType === -1) {
              return -1;
            }
            if (a.searchType === undefined || a.searchType === -1) {
              return 1;
            }
            return a.searchType - b.searchType;
          });

          this.newServiceIndex = 0;
          return filtered;
        },

        // Get some data from specific transaction

        /**
         * @param {number} id
         * @returns {string}
         * */
        transactionUrl(id) {
          if (globalThis.Terminated) {
            return globalThis.DetailServiceTransUrl.replace("/0", `/${id}`);
          }
          return globalThis.UpdateServiceTransUrl.replace("/0", `/${id}`);
        },

        /**
         * Get total amount
         * @param {ServiceTransaction} transaction
         * @returns {number}
         * */
        getAmount(transaction) {
          return transaction.quantity * transaction.price;
        },

        /**
         * Get total tax
         * @param {ServiceTransaction} transaction
         * @returns {number}
         * */
        getTax(transaction) {
          return (this.getAmount(transaction) * transaction.tax) / 100.0;
        },

        /**
         * Get total Price
         * @param {ServiceTransaction} transaction
         * @returns {number}
         * */
        getTotalPrice(transaction) {
          return this.getAmount(transaction) + this.getTax(transaction);
        },

        // Operations

        /**
         * Find a transaction by ID
         * @param {number} id
         * @returns {ServiceTransaction | undefined}
         * */
        findById(id) {
          const trans = this.transactions.find((trans) => trans.id == id);
          return trans;
        },

        /**
         * Find a transaction by service ID
         * @param {number} id
         * @returns {ServiceTransaction | undefined}
         * */
        findByServiceId(id) {
          const trans = this.transactions.find((p) => p.service.id == id);
          return trans;
        },

        // Adding

        /**
         * Add new transaction from service
         * @param {Service} service
         * */
        async addNewTransaction(service) {
          // this.closeNewServiceMode();
          service.transaction_loading = true;

          let addedTransaction = this.findByServiceId(service.id);

          if (!addedTransaction) {
            try {
              /**@type {ServiceTransactionCreation}*/
              const trans = {
                service_id: service.id,
                tax: service.transaction_tax ?? service.sell_tax,
                // tax: this.newServiceTax,
                quantity: service.transaction_quantity ?? 1,
                price: service.transaction_price ?? service.suggested_price,
              };
              console.log(trans);
              await serviceTransactionApiClient.addServiceTransaction(
                globalThis.OrderID,
                trans,
              );
            } catch (e) {
              console.log(e);
              // console.log(await e.text());
              globalThis.showNotify({
                title: "Error",
                msg: `Fail to create the new ${this.transactionType}`,
                status: "danger",
              });
            }
            await this.loadTransactions(false);

            addedTransaction = this.findByServiceId(service.id);
          }

          service.transaction_loading = false;
          this.focusSearch(true);
        },

        // Editing
        /**
         * save transaction
         * @param {ServiceTransaction} trans
         * */
        async save(trans) {
          if (!trans.id) return;
          trans.loading = true;
          try {
            await serviceTransactionApiClient.updateServiceTransaction(
              globalThis.OrderID,
              trans.id,
              {
                ...trans,
                service_id: trans.service.id,
              },
            );
          } catch (e) {
            console.error(e);
            // console.log(await e.text());
            globalThis.showNotify({
              title: "Error",
              msg: `Fail to update the ${globalThis.transactionType}`,
              status: "danger",
            });
            if (e instanceof Response) {
              console.error(await e.text());
            }
          }
          trans.loading = false;
          await this.loadTransactions(false);
        },

        /**
         * Execute a function on a transaction and save the transaction
         * @param {ServiceTransaction} trans
         * @param {Function} func
         * */
        async execAndSave(trans, func) {
          trans.loading = true;
          try {
            if (func) {
              func(trans);
            }
          } catch (e) {
            console.log(e);
          }
          await this.save(trans);
          trans.loading = false;
        },

        /**
         * Dec editing field
         * @param {ServiceTransaction} trans
         * @param {string} field
         * @param {number} [step]
         * @param {number} [min]
         * */
        dec(trans, field, step, min) {
          let fieldVal = trans[field];
          if (fieldVal === undefined) return;

          fieldVal = parseFloat(fieldVal) - (step ?? 1);
          if (min !== undefined) fieldVal = Math.max(fieldVal, min);
          fieldVal = parseFloat(fieldVal.toFixed(2));

          trans[field] = fieldVal;
        },

        /**
         * Dec editing field
         * @param {ServiceTransaction} trans
         * @param {string} field
         * @param {number} [step]
         * @param {number} [max]
         * */
        inc(trans, field, step, max) {
          let fieldVal = trans[field];
          if (fieldVal === undefined) return;

          fieldVal = parseFloat(fieldVal) + (step ?? 1);
          if (max !== undefined) fieldVal = Math.min(fieldVal, max);
          fieldVal = parseFloat(fieldVal.toFixed(2));

          trans[field] = fieldVal;
        },

        // Remove

        /**
         * @param {number} id
         * */
        remove(id) {
          this.toRemove = id;
        },

        removeCancel() {
          this.toRemove = -1;
        },

        async doRemove() {
          // this.loading = true;
          this.removing = true;
          try {
            await serviceTransactionApiClient.removeServiceTransaction(
              globalThis.OrderID,
              this.toRemove,
            );
            await this.loadTransactions(false);
            this.toRemove = -1;
          } catch (e) {
            console.error(e);
            globalThis.showNotify({
              title: "Error",
              msg: `Fail to remove the ${this.transactionType}`,
              status: "danger",
            });
          }
          // this.loading = false;
          this.removing = false;
        },

        showRemoveDialog() {
          return this.toRemove != -1;
        },

        /**
         * Get the name of the transaction marked for removal
         * @returns {string | null}
         * */
        getToRemoveName() {
          const transaction = this.findById(this.toRemove);
          if (!transaction) {
            return null;
          }
          return transaction.service.name;
        },

        // New services actions

        /**
         * Determinate if we are searching for new services
         * @returns {boolean}
         * */
        newServiceMode() {
          return this.newServiceSearch != "" || this.searchServiceInputFocus;
        },

        closeNewServiceMode() {
          this.newServiceSearch = "";
          this.searchServiceInputFocus = false;
          this.$refs.searchServices.blur();
        },

        // global close (close others dialogs)

        /**
         * Close all others instances
         * */
        closeAll() {
          if (!globalThis["closeAll"]) return;

          for (let close of globalThis["closeAll"]) {
            if (close) close();
          }
        },
      };
    });
  });
})();
