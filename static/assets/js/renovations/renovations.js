// @ts-check

/**@type {import('alpinejs').default}*/
var Alpine;

document.addEventListener("alpine:init", () => {
  Alpine.data("Renovations", () => {
    return {
      showNot7: true,
      showNot15: true,
      showUNot7: true,
      showUNot15: true,

      loading: false,
      sending: false,
      content: "",
      selected: -1,
      /**@type{string | null}*/
      error: null,
      notes: {},

      select(/**@type{number}*/ id) {
        this.selected = id;
        this.load();
      },

      showNotesModal() {
        return this.selected != -1;
      },

      closeNotesModal() {
        this.selected = -1;
      },

      async load() {
        this.loading = true;
        this.error = null;

        try {
          this.notes = await globalThis.loadNotes(this.selected);
        } catch (e) {
          console.error(e);
          this.error = "Fail to get contract notes";
        }

        this.loading = false;
        this.scrolldown();
      },

      async send() {
        this.sending = true;
        this.error = null;

        try {
          this.notes = await globalThis.pushNotes(this.selected, this.content);
          this.content = "";
        } catch (e) {
          console.error(e);
          this.error = "Fail to save contract note";
        }

        this.sending = false;
        this.scrolldown();
      },

      scrolldown() {
        setTimeout(() => {
          this.$refs.down.scrollIntoView({ behavior: "smooth" });
        }, 300);
      },
    };
  });
});
