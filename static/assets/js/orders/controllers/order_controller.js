// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

(function () {
  /** @typedef {import('../models/product_transaction.js').ProductTransaction} */
  /** @typedef {import('../models/product_transaction.js').ProductTransactionCreation} */
  /** @typedef {import('../models/product.js').Product} */

  const EditQuantity = "QTY";
  const EditPrice = "PRICE";
  const EditTax = "TAX";

  /**
   * Init a controller
   * @param {string} name - Identifier to use this controller from html
   * @param {string} productUrl - Base url to interact with products api
   * @param {string} productTransactionUrl - Base url to interact with products transaction api
   * @param {number} orderID
   * @param {string} shortcut - Key combination to use as shortcut
   * @param {string} transactionType - Transaction type to show on error notifications
   * */
  function _initController(
    name,
    productUrl,
    productTransactionUrl,
    orderID,
    shortcut,
    transactionType = "transaction",
  ) {
    document.addEventListener("alpine:init", () => {
      Alpine.data(name, () => {
        const productApiClient = new globalThis.ProductApiClient(productUrl);
        const productTransactionApiClient =
          new globalThis.ProductTransactionApiClient(productTransactionUrl);

        return {
          // Controller properties

          /** @type {boolean} */
          loadingProducts: false,
          /** @type {Array<Product>} */
          products: [],
          /** @type {string} */
          newProductSearch: "",
          /** @type {number} */
          newProductQty: 1,
          /** @type {boolean} */
          newProductTax: true,
          /** @type {boolean} */
          searchProductInputFocus: false,

          /** @type {boolean} */
          loading: false,

          /** @type {Array<ProductTransaction>} */
          transactions: [],
          /** @type {Array<ProductTransaction>} */
          satisfied: [],
          /** @type {Array<ProductTransaction>} */
          unsatisfied: [],

          satisfied_args: {
            total: 0,
            amount: 0,
            tax: 0,
          },
          unsatisfied_args: {
            total: 0,
            amount: 0,
            tax: 0,
          },

          selected: {
            id: -1,
            /** @type {ProductTransaction | undefined | null} */
            ref: null,
            editing: "",
          },

          toRemove: -1,
          removing: false,

          shortcut,
          transactionType,

          // Initialization
          init() {
            this.$watch("transactions", (transactions) => {
              this.satisfied_args.total = 0;
              this.satisfied_args.amount = 0;
              this.satisfied_args.tax = 0;

              this.unsatisfied_args.total = 0;
              this.unsatisfied_args.amount = 0;
              this.unsatisfied_args.tax = 0;

              for (let transaction of transactions) {
                const amount = this.getAmount(transaction);
                const tax = this.getTax(transaction);
                const total = amount + tax;
                if (transaction.satisfied) {
                  this.satisfied_args.total += total;
                  this.satisfied_args.amount += amount;
                  this.satisfied_args.tax += tax;
                } else {
                  this.unsatisfied_args.total += total;
                  this.unsatisfied_args.amount += amount;
                  this.unsatisfied_args.tax += tax;
                }
              }
            });
            this.loadTransactions();
            this.loadProducts();

            globalThis.bindShortcut(shortcut, () => {
              this.$refs.searchProducts.focus();
            });
            globalThis.bindShortcut("escape", () => {
              this.closeNewProductMode();
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
                await productTransactionApiClient.getProductTransactionList(
                  orderID,
                );
              this.satisfied = [];
              this.unsatisfied = [];
              this.transactions.forEach((transaction) => {
                if (transaction.satisfied) {
                  this.satisfied.push(transaction);
                } else {
                  this.unsatisfied.push(transaction);
                }
              });
            } catch (e) {
              console.error(e);
              if (loader) {
                globalThis.showNotify({
                  title: "Error",
                  msg: `Fail to load order's ${transactionType} list`,
                  status: "danger",
                });
              } else {
                globalThis.showNotify({
                  title: "Error",
                  msg: `Fail to reload order's ${transactionType} list`,
                  status: "danger",
                });
              }
            }
            if (loader) this.loading = false;
          },

          // Load Products
          async loadProducts() {
            this.loadingProducts = true;
            try {
              this.products = await productApiClient.getProducts();
            } catch (e) {
              console.error(e);
              globalThis.showNotify({
                title: "Error",
                msg: `Fail to load available ${transactionType} list`,
                status: "danger",
              });
            }
            this.loadingProducts = false;
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
          productUrl(id) {
            return globalThis.DetailProductUrl.replace("/0", `/${id}`);
          },

          /**
           * Get total amount
           * @param {ProductTransaction} transaction
           * @returns {number}
           * */
          getAmount(transaction) {
            return transaction.quantity * transaction.price;
          },

          /**
           * Get total tax
           * @param {ProductTransaction} transaction
           * @param {boolean?} force - if true will return the total tax without checking if active or not
           * @returns {number}
           * */
          getTax(transaction, force = false) {
            if (!force && !transaction.active_tax) return 0;
            return transaction.quantity * transaction.tax;
          },

          /**
           * Get total Price
           * @param {ProductTransaction} transaction
           * @returns {number}
           * */
          getTotalPrice(transaction) {
            return this.getAmount(transaction) + this.getTax(transaction);
          },

          /**
           * Get min Price
           * @param {ProductTransaction} transaction
           * @returns {number}
           * */
          getMinPrice(transaction) {
            const minPrice = transaction.product.min_price;
            const cost = transaction.cost;
            if (
              minPrice !== undefined &&
              minPrice !== null &&
              minPrice > cost
            ) {
              return minPrice;
            }
            return cost;
          },

          // Operations

          /**
           * Find a transaction by ID
           * @param {number} id
           * @returns {ProductTransaction | undefined}
           * */
          findById(id) {
            const trans = this.transactions.find((trans) => trans.id == id);
            return trans;
          },

          /**
           * Find a transaction by product ID
           * @param {number} id
           * @returns {ProductTransaction | undefined}
           * */
          findByProductId(id) {
            const trans = this.transactions.find((p) => p.product.id == id);
            return trans;
          },

          // Adding

          /**
           * Add new transaction from product
           * @param {Product} product
           * */
          async addNewTransaction(product) {
            /** @type {ProductTransactionCreation} */
            this.closeNewProductMode();

            let addedTransaction = this.findByProductId(product.id);

            if (!addedTransaction) {
              try {
                const trans = {
                  product_id: product.id,
                  tax: product.sell_tax,
                  active_tax: this.newProductTax,
                  quantity: this.newProductQty,
                  price: product.sell_price,
                };
                console.log(trans);
                await productTransactionApiClient.addProductTransaction(
                  orderID,
                  trans,
                );
              } catch (e) {
                console.log(e);
                // console.log(await e.text());
                globalThis.showNotify({
                  title: "Error",
                  msg: `Fail to create the new ${transactionType}`,
                  status: "danger",
                });
              }
              await this.loadTransactions(false);

              addedTransaction = this.findByProductId(product.id);
            }

            this.select(addedTransaction);
          },

          // Editing
          /**
           * Edit save
           * @param {ProductTransaction} ref
           * */
          async editSave(ref) {
            if (!ref.id) return;
            ref.price = Math.max(ref.price, this.getMinPrice(ref));
            try {
              await productTransactionApiClient.updateProductTransaction(
                orderID,
                ref.id,
                {
                  ...ref,
                  product_id: ref.product.id,
                },
              );
            } catch (e) {
              console.error(e);
              // console.log(await e.text());
              globalThis.showNotify({
                title: "Error",
                msg: `Fail to update the ${transactionType}`,
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
           * @param {ProductTransaction | undefined} transaction
           * @returns {ProductTransaction | undefined}
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
           * @returns {ProductTransaction | undefined}
           * */
          selectById(id) {
            const trans = this.findById(id);
            return this.select(trans);
          },

          /**
           * Get the editing field value
           * @returns {number | undefined}
           * */
          getEditingField() {
            if (!this.selected.ref) return undefined;

            switch (this.selected.editing) {
              case EditQuantity:
                return this.selected.ref.quantity;
              case EditPrice:
                return this.selected.ref.price;
            }
          },

          /**
           * Set the editing field value
           * @param {number} val
           * */
          setEditingField(val) {
            if (!this.selected.ref) return undefined;

            switch (this.selected.editing) {
              case EditQuantity:
                this.selected.ref.quantity = val;
                break;
              case EditPrice:
                this.selected.ref.price = val;
                break;
            }
          },

          /**
           * Dec editing field
           * @param {number} [step]
           * @param {number} [min]
           * */
          decEditingField(step, min) {
            let fieldVal = this.getEditingField();
            if (fieldVal === undefined) return;

            fieldVal = parseInt(fieldVal) - (step ?? 1);
            if (min !== undefined) fieldVal = Math.max(fieldVal, min);

            this.setEditingField(fieldVal);
          },

          /**
           * Dec editing field
           * @param {number} [step]
           * @param {number} [max]
           * */
          incEditingField(step, max) {
            let fieldVal = this.getEditingField();
            if (fieldVal === undefined) return;

            fieldVal = parseInt(fieldVal) + (step ?? 1);
            if (max !== undefined) fieldVal = Math.min(fieldVal, max);

            this.setEditingField(fieldVal);
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
              await productTransactionApiClient.removeProductTransaction(
                orderID,
                this.toRemove,
              );
              await this.loadTransactions(false);
              this.toRemove = -1;
            } catch (e) {
              console.error(e);
              globalThis.showNotify({
                title: "Error",
                msg: `Fail to remove the ${transactionType}`,
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
            return transaction.product.name;
          },

          // New products actions

          /**
           * Determinate if we are searching for new products
           * @returns {boolean}
           * */
          newProductMode() {
            return this.newProductSearch != "" || this.searchProductInputFocus;
          },

          closeNewProductMode() {
            this.newProductSearch = "";
            this.searchProductInputFocus = false;
            this.$refs.searchProducts.blur();
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
  }

  globalThis.initController = _initController;
})();
