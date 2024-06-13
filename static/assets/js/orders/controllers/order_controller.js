// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

(function () {
  /** @typedef {import('../models/product_transaction.js').ProductTransaction} */
  /** @typedef {import('../models/product_transaction.js').ProductTransactionCreation} */
  /** @typedef {import('../models/product.js').Product} */

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
          // /** @type {number} */
          // newProductQty: 1,
          // /** @type {boolean} */
          // newProductTax: true,
          /** @type {boolean} */
          searchProductInputFocus: false,

          /** @type {boolean} */
          loading: false,

          /** @type {Array<number>} */
          transactionsProducts: [],
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

              this.transactionsProducts = [];

              for (let transaction of transactions) {
                if (
                  this.transactionsProducts.indexOf(transaction.product.id) ==
                  -1
                )
                  this.transactionsProducts.push(transaction.product.id);

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
              this.closeAll();
              this.$refs.searchProducts.focus();
            });
            globalThis.bindShortcut("escape", () => {
              this.closeNewProductMode();
            });

            const closeThis = () => {
              this.closeNewProductMode();
            };
            if (globalThis["closeAll"]) {
              globalThis["closeAll"].push(closeThis);
            } else {
              globalThis["closeAll"] = [closeThis];
            }

            globalThis[`reload_${this.transactionType}`] = () => {
              this.loadTransactions;
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
              for (let product of this.products) {
                product.transaction_quantity = 1;
                product.transaction_price = product.sell_price;
                // product.suggested_price > product.sell_price
                //   ? product.suggested_price
                //   : product.sell_price;
                product.transaction_tax = true;
              }
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
           * Render product, return true if should be rendered
           * @param {Product} product
           * @returns {boolean}
           * */
          renderProduct(product) {
            return this.transactionsProducts.indexOf(product.id) == -1;
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
            // this.closeNewProductMode();
            product.transaction_loading = true;

            let addedTransaction = this.findByProductId(product.id);

            if (!addedTransaction) {
              try {
                /** @type {ProductTransactionCreation} */
                const trans = {
                  product_id: product.id,
                  tax: product.sell_tax,
                  active_tax: product.transaction_tax ?? false,
                  quantity: product.transaction_quantity ?? 1,
                  price: product.transaction_price ?? product.sell_price,
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

            product.transaction_loading = false;
          },

          // Editing
          /**
           * save transaction
           * @param {ProductTransaction} trans
           * */
          async save(trans) {
            if (!trans.id) return;
            trans.loading = true;
            trans.price = Math.max(trans.price, this.getMinPrice(trans));
            try {
              await productTransactionApiClient.updateProductTransaction(
                orderID,
                trans.id,
                {
                  ...trans,
                  product_id: trans.product.id,
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
            trans.loading = false;
            await this.loadTransactions(false);
          },

          /**
           * Execute a function on a transaction and save the transaction
           * @param {ProductTransaction} trans
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
           * @param {ProductTransaction} trans
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
           * @param {ProductTransaction} trans
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

          /**
           * focus element
           * @param {HTMLElement} el
           * @param {boolean} [scroll]
           * */
          focusElement(el, scroll) {
            el.focus();
            if (scroll) this.scrollTo(el);
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
        };
      });
    });
  }

  globalThis.initController = _initController;
})();
