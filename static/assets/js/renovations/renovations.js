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

        this.notes = await globalThis.loadNotes(this.selected);
        console.log(this.notes);

        this.loading = false;
      },

      async send() {
        this.sending = true;

        this.notes = await globalThis.pushNotes(this.selected, this.content);
        console.log(this.notes);
        this.content = "";

        this.sending = false;
      },
    };
  });
});
