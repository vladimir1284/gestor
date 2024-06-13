// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

(function () {
  /** @typedef {import('../models/service_transaction.js').ServiceTransaction} */
  /** @typedef {import('../models/service_transaction.js').ServiceTransactionCreation} */
  /** @typedef {import('../models/service.js').Service} */

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

        /** @type {boolean} */
        loadingServices: false,
        /** @type {Array<Service>} */
        services: [],
        /** @type {string} */
        newServiceSearch: "",
        /** @type {number} */
        newServiceQty: 1,
        /** @type {number} */
        newServiceTax: 0,
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
          });
          this.loadTransactions();
          this.loadServices();

          globalThis.bindShortcut(this.shortcut, () => {
            this.closeAll();
            this.$refs.searchServices.focus();
          });
          globalThis.bindShortcut("escape", () => {
            this.closeNewServiceMode();
          });

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
          return transaction.quantity * transaction.tax;
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

        // Tools
        /**
         * Scroll to element
         * @param {HTMLElement} el
         * */
        scrollTo(el) {
          console.log(el);
          setTimeout(() => {
            el.scrollIntoView({ behavior: "smooth" });
          }, 300);
        },
      };
    });
  });
})();
