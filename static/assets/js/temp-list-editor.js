function getData() {
    const element = document.querySelector("#id_text");
    const content = element.value;

    try {
        return JSON.parse(content);
    } catch (e) {
        console.log(e);
        return [];
    }
}

function setData(data) {
    const element = document.querySelector("#id_text");
    element.value = data;

    const form = document.querySelector("#form");
    form.submit();
}

document.addEventListener("alpine:init", () => {
    Alpine.data("tempList", () => ({
        data: getData(),
        sortKP: {},
        selected: -1,
        toRemove: -1,

        newItem() {
            this.selected = -1;
            this.data.push("New item");
            this.selected = this.data.length - 1;
        },

        save() {
            const data = JSON.stringify(this.data);
            setData(data);
        },

        unselect() {
            this.selected = -1;
        },

        select(id) {
            if (this.selected == id) {
                this.unselect();
                return;
            }
            this.selected = id;
        },

        setToRemove(id) {
            if (id >= this.data.length || id < 0) {
                id = -1;
            }
            this.toRemove = id;
        },

        remove() {
            if (this.toRemove >= this.data.length || this.toRemove < 0) {
                return;
            }
            this.selected = -1;
            this.data.splice(this.toRemove, 1);
            this.toRemove = -1;
        },
    }));
});
