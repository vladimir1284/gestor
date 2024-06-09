// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

(function () {
  /** @typedef {import('../models/service_transaction.js').ServiceTransaction} */
  /** @typedef {import('../models/service_transaction.js').ServiceTransactionCreation} */
  /** @typedef {import('../models/service.js').Service} */

  const EditQuantity = "QTY";
  const EditPrice = "PRICE";
  const EditTax = "TAX";

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
        /** @type {boolean} */
        newServiceTax: true,
        /** @type {boolean} */
        searchServiceInputFocus: false,

        /** @type {boolean} */
        loading: false,

        /** @type {Array<ServiceTransaction>} */
        transactions: [],
        transactions_args: {
          total: 0,
          amount: 0,
          tax: 0,
        },

        selected: {
          id: -1,
          /** @type {ServiceTransaction | undefined | null} */
          ref: null,
          editing: "",
        },

        toRemove: -1,
        removing: false,

        shortcut: "alt+s",
        transactionType: "service",

        // Initialization
        init() {
          this.$watch("transactions", (transactions) => {
            for (let transaction of transactions) {
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
            this.$refs.searchServices.focus();
          });
          globalThis.bindShortcut("escape", () => {
            this.newServiceSearch = "";
            this.$refs.searchServices.blur();
            this.editNothing();
          });
          globalThis.bindShortcut("enter", () => {
            this.editNothing();
          });
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

        // Get some data from specific transaction

        /**
         * @param {number} id
         * @returns {string}
         * */
        transactionUrl(id) {
          if (globalThis.Terminated) {
            return globalThis.DetailTransUrl.replace("/0", `/${id}`);
          }
          return globalThis.UpdateTransUrl.replace("/0", `/${id}`);
        },

        /**
         * @param {number} id
         * @returns {string}
         * */
        serviceUrl(id) {
          return globalThis.DetailServiceUrl.replace("/0", `/${id}`);
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
          /** @type {ServiceTransactionCreation} */
          this.newServiceSearch = "";

          let addedTransaction = this.findByServiceId(service.id);

          if (!addedTransaction) {
            try {
              /**@type {ServiceTransactionCreation}*/
              const trans = {
                service_id: service.id,
                tax: service.sell_tax,
                quantity: this.newServiceQty,
                price: service.suggested_price,
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

          this.select(addedTransaction);
        },

        // Editing
        /**
         * Edit save
         * @param {ServiceTransaction} ref
         * */
        async editSave(ref) {
          if (!ref.id) return;
          try {
            await serviceTransactionApiClient.updateServiceTransaction(
              globalThis.OrderID,
              ref.id,
              {
                ...ref,
                service_id: ref.service.id,
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
          await this.loadTransactions(false);
        },

        /**
         * If an element was selected saved
         * */
        async checkEditingSave() {
          if (this.selected.ref) this.editSave(this.selected.ref);
        },

        /**
         * Edit nothing
         * */
        editNothing() {
          this.checkEditingSave();

          this.selected.id = -1;
          this.selected.ref = null;
          this.selected.editing = "";
        },

        /**
         * Select a transaction if exist
         * @param {ServiceTransaction | undefined} transaction
         * @returns {ServiceTransaction | undefined}
         * */
        select(transaction) {
          this.checkEditingSave();

          if (
            transaction &&
            transaction.id &&
            transaction.id != this.selected.id
          ) {
            this.selected.id = transaction.id;
            this.selected.ref = transaction;
            this.selected.editing = "";
          }
          return transaction;
        },

        /**
         * Select a transaction if exist by id
         * @param {number} id
         * @returns {ServiceTransaction | undefined}
         * */
        selectById(id) {
          const trans = this.findById(id);
          return this.select(trans);
        },

        /**
         * Edit transaction quantity
         * @param {number} id
         * */
        editQuantity(id) {
          this.selectById(id);
          this.selected.editing = EditQuantity;
        },

        /**
         * Edit transaction price
         * @param {number} id
         * */
        editPrice(id) {
          this.selectById(id);
          this.selected.editing = EditPrice;
        },

        /**
         * Edit transaction tax
         * @param {number} id
         * */
        editTax(id) {
          this.selectById(id);
          this.selected.editing = EditTax;
        },

        /**
         * Check if editing transaction quantity
         * @param {number} id
         * @returns {boolean}
         * */
        editingQuantity(id) {
          return (
            this.selected.id == id && this.selected.editing == EditQuantity
          );
        },

        /**
         * Check if editing transaction price
         * @param {number} id
         * @returns {boolean}
         * */
        editingPrice(id) {
          return this.selected.id == id && this.selected.editing == EditPrice;
        },

        /**
         * Check if editing transaction tax
         * @param {number} id
         * @returns {boolean}
         * */
        editingTax(id) {
          return this.selected.id == id && this.selected.editing == EditTax;
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
              globalThis.orderID,
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
