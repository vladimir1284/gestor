// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

(function () {
  /** @typedef {import('../models/product_transaction.js').ProductTransaction} */
  /** @typedef {import('../models/product_transaction.js').ProductTransactionCreation} */
  /** @typedef {import('../models/product.js').Product} */

  const NONE = 0;
  const QTY = 1;
  const PRICE = 2;
  const TAX = 3;
  const EditMIN = NONE;
  const EditMAX = TAX;

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
          /** @type {{shortcut: string[], description: string[]}[]} */
          shortcutHelper: [],

          /** @type {boolean} */
          loadingProducts: false,
          /** @type {Array<Product>} */
          products: [],
          /** @type {Array<Product>} */
          filteredProducts: [],
          /** @type {string} */
          newProductSearch: "",
          /** @type {number} */
          newProductIndex: 0,
          /** @type {number} */
          newProductEditing: NONE,
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

          /** @type {number} */
          lastScrollTimeout: -1,
          /** @type {number} */
          lastSelectTimeout: -1,

          // Initialization
          init() {
            if (!globalThis.globalPSC) {
              globalThis.globalPSC = Alpine.reactive({});
            }
            globalThis.globalPSC[this.transactionType] = this;
            // this.$store.globalPSC[this.transactionType] = this;
            // Init observers
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
              this.filteredProducts = this.getFiltered();
            });

            this.$watch("newProductSearch", () => {
              this.filteredProducts = this.getFiltered();
            });

            // Load elements
            this.loadTransactions();
            this.loadProducts();

            // global close this
            const closeThis = () => {
              this.closeNewProductMode();
            };
            if (globalThis["closeAll"]) {
              globalThis["closeAll"].push(closeThis);
            } else {
              globalThis["closeAll"] = [closeThis];
            }

            globalThis[`reload_${this.transactionType}`] = () =>
              this.loadTransactions();

            // Shortcuts
            /** @type {{shortcut: string | string[], func: function, description: string | string[], direct?: boolean}[]} */
            const shortcuts = [
              {
                shortcut: this.shortcut,
                description: [
                  `Open the dialog to add new products of type ${transactionType}`,
                  `Abrir el dialogo para agregar nuevos productos de tipo ${transactionType}`,
                ],
                func: () => {
                  this.closeAll();
                  this.$refs.searchProducts.focus();
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
                func: () => this.closeNewProductMode(),
              },
              {
                shortcut: "Enter",
                description: [
                  "Add the selected product",
                  "Agregar el producto seleccionado",
                ],
                func: () =>
                  this.addNewTransaction(
                    this.filteredProducts[this.newProductIndex],
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
                  "Select the previous product on the list",
                  "Seleccionar el producto anterior en la lista",
                ],
                func: () => this.selectPreviousItem(),
              },
              {
                shortcut: ["Alt+ArrowDown", "ArrowDown"],
                description: [
                  "Select the next product on the list",
                  "Seleccionar el producto siguiente en la lista",
                ],
                func: () => this.selectNextItem(),
              },
              {
                shortcut: ["Tab", "Alt+Tab", "Alt+ArrowRight"],
                description: [
                  "Focus the next editable (quantity, price and tax) on the selected product",
                  "Enfocar el siguiente editable (cantidad, precio y impuesto) del producto seleccionado",
                ],
                func: () => this.focusNextEditableOfSelected(),
              },
              {
                shortcut: ["Alt+ArrowLeft"],
                description: [
                  "Focus the previous editable (quantity, price and tax) on the selected product",
                  "Enfocar el anterior editable (cantidad, precio y impuesto) del producto seleccionado",
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
            clearTimeout(this.lastScrollTimeout);
            this.lastScrollTimeout = setTimeout(() => {
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
              clearTimeout(this.lastSelectTimeout);
              this.lastSelectTimeout = setTimeout(() => {
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
            globalThis.bindShortcut(
              shortcut,
              (/**@type {KeyboardEvent}*/ e) => {
                if (!this.newProductMode()) {
                  return;
                }
                e.preventDefault();
                callback();
              },
            );
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
            this.newProductEditing = EditMIN;
            const input = /**@type {HTMLInputElement}*/ (
              this.$refs.searchProducts
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
              document.querySelectorAll(".product_editable.product_active")
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
                `.product_editable.product_active.product_selected.product_${type}`,
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
            this.newProductEditing++;
            if (this.newProductEditing > EditMAX) {
              this.newProductEditing = EditMIN;
            }
            this.blurFocusEditable(this.newProductEditing);
          },

          /**
           * Focus previous editable of selected element
           * */
          focusPreviousEditableOfSelected() {
            this.newProductEditing--;
            if (this.newProductEditing < EditMIN) {
              this.newProductEditing = EditMAX;
            }
            this.blurFocusEditable(this.newProductEditing);
          },

          // Selector tools

          /**
           * Select next item
           * */
          selectNextItem() {
            this.newProductIndex++;
            if (this.newProductIndex >= this.filteredProducts.length) {
              this.newProductIndex = this.filteredProducts.length - 1;
            }
            this.newProductEditing = NONE;
            this.blurEditables();
          },

          /**
           * Select next item
           * */
          selectPreviousItem() {
            this.newProductIndex--;
            if (this.newProductIndex < 0) {
              this.newProductIndex = 0;
            }
            this.newProductEditing = NONE;
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
          /**
           * @param {boolean} [reload]
           * */
          async loadProducts(reload) {
            if (!reload) this.loadingProducts = true;
            try {
              this.products = await productApiClient.getProducts();
              for (let product of this.products) {
                product.transaction_quantity = 1;
                product.transaction_price = product.sell_price;
                product.transaction_tax = true;
              }
              this.filteredProducts = this.getFiltered();
            } catch (e) {
              console.error(e);
              globalThis.showNotify({
                title: "Error",
                msg: `Fail to load available ${transactionType} list`,
                status: "danger",
              });
            }
            if (!reload) this.loadingProducts = false;
          },

          // Get filter elements
          /**
           * @returns {Array<Product>}
           * */
          getFiltered() {
            let filtered = this.products.filter((p) => {
              const st = globalThis.advanceMatch(p.name, this.newProductSearch);
              p.searchType = st;
              return this.renderProduct(p) && st !== undefined && st !== -1;
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

            this.newProductIndex = 0;
            return filtered;
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
            return (this.getAmount(transaction) * transaction.tax) / 100.0;
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
            return transaction.product.sell_price;
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
                globalThis.showNotify({
                  title: "Error",
                  msg: `Fail to create the new ${transactionType}`,
                  status: "danger",
                });
              }
              await this.loadTransactions(false);
              await this.loadProducts(true);

              addedTransaction = this.findByProductId(product.id);
            }

            product.transaction_loading = false;
            this.focusSearch(true);
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
            this.newProductIndex = 0;
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
  }

  globalThis.initController = _initController;
})();
