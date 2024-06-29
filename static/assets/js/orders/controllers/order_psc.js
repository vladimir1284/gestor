// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

/** @typedef {import('../models/kit.js').NewKit} */
/**
 * @param {NewKit} kit
 * */
async function createNewKit(kit) {
  const csrftoken = globalThis.getCookie("csrftoken");
  const resp = await fetch(`${globalThis.KitUrl}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrftoken ? csrftoken : "",
      "content-type": "application/json",
    },
    credentials: "same-origin",
    body: JSON.stringify(kit),
  });
  if (resp.status != 200 && resp.status != 201 && resp.status != 204) {
    throw resp;
  }
}

function init() {
  if (globalThis._orderPSC) return;
  globalThis._orderPSC = true;

  /** @typedef {import('../models/product_transaction.js').ProductTransaction} */
  /** @typedef {import('../models/service_transaction.js').ServiceTransaction} */

  // Alpine.store("globalPSC", {});
  Alpine.data("OrderPSC", () => {
    return {
      psc: globalThis.globalPSC,
      kits: null,
      parts: null,
      services: null,
      consumables: null,

      /** @type {string} */
      newKitName: "",
      /** @type {boolean} */
      newKit: false,
      /** @type {boolean} */
      creatingNewKit: false,

      init() {
        Alpine.effect(() => {
          this.kits = this.psc.kit;
        });
        Alpine.effect(() => {
          this.parts = this.psc.part;
        });
        Alpine.effect(() => {
          this.services = this.psc.service;
        });
        Alpine.effect(() => {
          this.consumables = this.psc.consumable;
        });

        // globalThis.bindShortcut("Alt+Shift+K", () => this.newKitMode());
        // globalThis._pscObjThis = this;
        // globalThis.bindShortcut("Enter", {
        //   func: () => {
        //     if (!globalThis._pscObjThis.showNewKitDialog()) return;
        //
        //     globalThis._pscObjThis.createNewKit();
        //     return true;
        //   },
        //   priority: 5,
        // });
        // globalThis.bindShortcut("Escape", {
        //   func: () => {
        //     if (!globalThis._pscObjThis.showNewKitDialog()) return;
        //
        //     globalThis._pscObjThis.newKitCancel();
        //     return true;
        //   },
        //   priority: 5,
        // });
      },

      // Parts
      getParts() {
        if (!this.parts) {
          return [];
        }
        /** @type {Array<ProductTransaction>} */
        const transactions = this.parts.transactions;
        return transactions.sort((a, b) => {
          return (b.id ?? -1) - (a.id ?? -1);
        });
      },

      // Services
      getServices() {
        if (!this.services) {
          return [];
        }
        /** @type {Array<ServiceTransaction>} */
        const transactions = this.services.transactions;
        return transactions.sort((a, b) => {
          return (b.id ?? -1) - (a.id ?? -1);
        });
      },

      // Consumables
      getConsumables() {
        if (!this.consumables) {
          return [];
        }
        /** @type {Array<ProductTransaction>} */
        const transactions = this.consumables.transactions;
        return transactions.sort((a, b) => {
          return (b.id ?? -1) - (a.id ?? -1);
        });
      },

      // Kits
      showNewKitDialog() {
        return this.newKit;
      },

      newKitMode() {
        this.newKit = true;
        this.newKitName = "";
        setTimeout(() => this.$refs.newKitNameInput.focus(), 100);
      },

      newKitCancel() {
        this.newKit = false;
        this.newKitName = "";
      },

      async createNewKit() {
        console.log(this.newKitName);
        if (this.newKitName === "") {
          globalThis.showNotify({
            title: "Error",
            msg: "Please, write a name for the KIT.",
            status: "danger",
          });
          return;
        }

        this.creatingNewKit = true;
        /** @type {NewKitElement[]} */
        const parts = this.getParts()
          .filter((v) => v.select_for_kit)
          .map((v) => {
            return {
              product: v.product,
              quantity: v.quantity,
            };
          });
        /** @type {NewKitElement[]} */
        const consumables = this.getConsumables()
          .filter((v) => v.select_for_kit)
          .map((v) => {
            return {
              product: v.product,
              quantity: v.quantity,
            };
          });
        /** @type {NewKitService[]} */
        const services = this.getServices()
          .filter((v) => v.select_for_kit)
          .map((v) => {
            return {
              service: v.service,
            };
          });

        /** @type {NewKit} */
        const kit = {
          name: this.newKitName,
          services,
          elements: [...parts, ...consumables],
        };

        try {
          await createNewKit(kit);
          if (this.kits) this.kits.loadKits();
          this.newKitCancel();
        } catch (e) {
          console.error(e);
          let notified = false;
          if (e instanceof Response) {
            try {
              const data = await e.json();
              console.error(data);
              if ("name" in data) {
                let errors = "<ul>";
                for (let msg of data["name"]) {
                  errors += "<li>" + msg + "</li>";
                }
                errors += "</ul>";
                globalThis.showNotify({
                  title: "Error",
                  msg: "Fail to create the kit:" + errors,
                  status: "danger",
                });
                notified = true;
              }
            } catch (e) {
              console.error(await e.text());
            }
          }
          if (!notified) {
            globalThis.showNotify({
              title: "Error",
              msg: "Fail to create the kit",
              status: "danger",
            });
          }
        }
        this.creatingNewKit = false;
      },
    };
  });
}

document.addEventListener("alpine:init", init);
