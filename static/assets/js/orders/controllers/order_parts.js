// @ts-check

/** @typedef {import('../models/product_transaction.js').ProductTransaction} */
/** @typedef {import('../models/product.js').Product} */

/** @type {import('alpinejs').default} */
var Alpine;

const EditQuantity = "QTY";
const EditTax = "TAX";

document.addEventListener("alpine:init", () => {
  Alpine.data("OrderParts", () => {
    return {
      // Controller properties

      /** @type {boolean} */
      loadingPartsProducts: false,
      /** @type {Array<Product>} */
      partsProducts: [],
      /** @type {string} */
      searchNewProduct: "",

      /** @type {boolean} */
      loading: false,

      /** @type {Array<ProductTransaction>} */
      parts: [],
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

      // Initialization
      init() {
        this.$watch("parts", (parts) => {
          this.satisfied_args.total = 0;
          this.satisfied_args.amount = 0;
          this.satisfied_args.tax = 0;

          this.unsatisfied_args.total = 0;
          this.unsatisfied_args.amount = 0;
          this.unsatisfied_args.tax = 0;

          for (let p of parts) {
            const amount = this.getAmount(p);
            const tax = this.getTax(p);
            const total = amount + tax;
            if (p.satisfied) {
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
        this.loadParts();
        this.loadPartsProducts();
      },

      // Load data
      async loadParts(loader = true) {
        if (loader) this.loading = true;
        try {
          this.parts = await globalThis.getOrderParts(globalThis.OrderID);
          this.satisfied = [];
          this.unsatisfied = [];
          this.parts.forEach((p) => {
            if (p.satisfied) {
              this.satisfied.push(p);
            } else {
              this.unsatisfied.push(p);
            }
          });
        } catch (e) {
          console.error(e);
        }
        if (loader) this.loading = false;
      },

      // Load PartsProducts
      async loadPartsProducts() {
        this.loadingPartsProducts = true;
        try {
          this.partsProducts = await globalThis.getPartProducts();
          console.log(this.partsProducts);
        } catch (e) {
          console.error(e);
        }
        this.loadingPartsProducts = false;
      },

      // Get some data from specific part

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
       * @param {ProductTransaction} part
       * @returns {number}
       * */
      getAmount(part) {
        return part.quantity * part.price;
      },

      /**
       * Get total tax
       * @param {ProductTransaction} part
       * @param {boolean?} force - if true will return the total tax without checking if active or not
       * @returns {number}
       * */
      getTax(part, force = false) {
        if (!force && !part.active_tax) return 0;
        return part.quantity * part.tax;
      },

      /**
       * Get total Price
       * @param {ProductTransaction} part
       * @returns {number}
       * */
      getTotalPrice(part) {
        return this.getAmount(part) + this.getTax(part);
      },

      // Operations

      /**
       * Find a part by ID
       * @param {number} id
       * @returns {ProductTransaction | undefined}
       * */
      findById(id) {
        const part = this.parts.find((p) => p.id == id);
        return part;
      },

      // Editing
      /**
       * Edit save
       * @param {ProductTransaction} ref
       * */
      async editSave(ref) {
        console.log(ref);
        try {
          const resp = await globalThis.updateOrderParts(
            globalThis.OrderID,
            ref,
          );
          console.log(resp);
        } catch (e) {
          console.error(e);
          console.log(await e.text());
        }
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
       * Edit part quantity
       * @param {number} id
       * */
      editQuantity(id) {
        this.checkEditingSave();

        this.selected.id = id;
        this.selected.ref = this.findById(id);
        this.selected.editing = EditQuantity;
      },

      /**
       * Edit part tax
       * @param {number} id
       * */
      editTax(id) {
        this.checkEditingSave();

        this.selected.id = id;
        this.selected.ref = this.findById(id);
        this.selected.editing = EditTax;
      },

      /**
       * Check if editing part quantity
       * @param {number} id
       * @returns {boolean}
       * */
      editingQuantity(id) {
        return this.selected.id == id && this.selected.editing == EditQuantity;
      },

      /**
       * Check if editing part tax
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
          await globalThis.removeOrderParts(globalThis.OrderID, this.toRemove);
          await this.loadParts(false);
          this.toRemove = -1;
        } catch (e) {
          console.error(e);
        }
        // this.loading = false;
        this.removing = false;
      },

      showRemoveDialog() {
        return this.toRemove != -1;
      },

      /**
       * Get the name of the part marked for removal
       * @returns {string | null}
       * */
      getToRemoveName() {
        const part = this.findById(this.toRemove);
        if (!part) {
          return null;
        }
        return part.product.name;
      },

      // New products actions

      /**
       * Determinate if we are searching for new products
       * @returns {boolean}
       * */
      newProductMode() {
        return this.searchNewProduct != "";
      },
    };
  });
});
