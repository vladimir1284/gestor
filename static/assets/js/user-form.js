const Roles = window.jroles;

const roles = document.querySelectorAll(
    '#div_id_groups input[type="checkbox"]',
);
const menu = document.querySelectorAll('#menu_perms input[type="checkbox"]');
const urls = document.querySelectorAll('#urls_perms input[type="checkbox"]');
const dash = document.querySelectorAll(
    '#dashboard_card_perms input[type="checkbox"]',
);
const extra = document.querySelectorAll('#extra_perms input[type="checkbox"]');

const accordionCollapse = document.querySelectorAll(
    ".accordion-collapse.collapse",
);
const accordionButton = document.querySelectorAll(
    ".accordion-button.collapsed",
);

accordionCollapse.forEach((ac) => {
    ac.setAttribute(":class", '{show: $store.search.search != ""}');
});
accordionButton.forEach((ac) => {
    ac.setAttribute(":class", '{collapsed: $store.search.search == ""}');
});

const refs = [];

roles.forEach((r) => {
    r.setAttribute("x-model", `model.role_${r.value}`);
    r.classList.add("checkboxinput");
    r.parentNode.setAttribute("x-show", "() => match($el)");
});

function initPerms(perms, model) {
    perms.forEach((e) => {
        const ref = `perm.${e.dataset["perm"]}`;
        const xmodel = `${model}.${e.dataset["perm"]}`;
        refs.push(ref);
        e.setAttribute("x-ref", ref);
        e.setAttribute("x-model", xmodel);
        e.parentNode.setAttribute("x-show", "() => match($el)");
    });
}

initPerms(menu, "menu");
initPerms(urls, "urls");
initPerms(dash, "dash");
initPerms(extra, "extra");

function getARPerms(m) {
    const perms = [];
    Roles.forEach((r) => {
        if (!m[`role_${r.id}`]) return;

        r.permissions.forEach((p) => {
            if (perms.indexOf(p) == -1) {
                perms.push(p);
            }
        });
    });
    return perms;
}

function getState(elements) {
    let mark = false;
    let unmark = false;
    for (let k in elements) {
        if (elements[k]) {
            mark = true;
        } else {
            unmark = true;
        }
    }

    if (mark && !unmark) {
        return 1;
    } else if (!mark && unmark) {
        return 0;
    } else {
        return -1;
    }
}

document.addEventListener("alpine:init", () => {
    Alpine.data("UserRolesPerms", () => {
        return {
            model: {},
            menu: {},
            urls: {},
            dash: {},
            extra: {},

            init() {
                this.$watch("model", (m) => {
                    this.updateAllRoles(m);
                    this.updatePerms(m);
                });
                this.$watch("menu", (m) => {
                    this.updateMenuAll(m);
                });
                this.$watch("urls", (m) => {
                    this.updateUrlsAll(m);
                });
                this.$watch("dash", (m) => {
                    this.updateDashAll(m);
                });
                this.$watch("extra", (m) => {
                    this.updateExtraAll(m);
                });
                roles.forEach((r) => {
                    this.model[`role_${r.value}`] = r.checked;
                });
                menu.forEach((p) => {
                    this.menu[p.dataset["perm"]] = p.checked;
                });
                urls.forEach((p) => {
                    this.urls[p.dataset["perm"]] = p.checked;
                });
                dash.forEach((p) => {
                    this.dash[p.dataset["perm"]] = p.checked;
                });
                extra.forEach((p) => {
                    this.extra[p.dataset["perm"]] = p.checked;
                });
            },

            updatePerms(m) {
                const perms = getARPerms(m);
                let menu = false;
                let urls = false;
                let dash = false;
                let extra = false;
                refs.forEach((r) => {
                    const e = this.$refs[r];
                    const p = e.dataset["perm"];
                    if (perms.indexOf(p) != -1) {
                        e.disabled = true;
                        e.parentNode.classList.add("disabled");
                    } else {
                        if (p.startsWith("menu___")) {
                            menu = true;
                        }
                        if (p.startsWith("urls___")) {
                            urls = true;
                        }
                        if (p.startsWith("dashboard_card___")) {
                            dash = true;
                        }
                        if (p.startsWith("extra_perm___")) {
                            extra = true;
                        }
                        e.disabled = false;
                        e.parentNode.classList.remove("disabled");
                    }
                });

                this.$refs.menu_all.disabled = !menu;
                this.$refs.urls_all.disabled = !urls;
                this.$refs.dash_all.disabled = !dash;
                this.$refs.extra_all.disabled = !extra;
            },

            setStateOf(input, elements) {
                const state = getState(elements);
                if (state == 1) {
                    input.checked = true;
                    input.indeterminate = false;
                } else if (state == 0) {
                    input.checked = false;
                    input.indeterminate = false;
                } else {
                    input.checked = true;
                    input.indeterminate = true;
                }
            },

            updateAllRoles(m) {
                this.setStateOf(this.$refs.all_roles, m);
            },

            updateMenuAll(m) {
                this.setStateOf(this.$refs.menu_all, m);
            },

            updateUrlsAll(m) {
                this.setStateOf(this.$refs.urls_all, m);
            },

            updateDashAll(m) {
                this.setStateOf(this.$refs.dash_all, m);
            },

            updateExtraAll(m) {
                this.setStateOf(this.$refs.extra_all, m);
            },

            toggleAllRoles() {
                const state = this.$el.checked;
                for (let k in this.model) {
                    this.model[k] = state;
                }
            },

            toggleMenuAll() {
                const state = this.$el.checked;
                for (let k in this.menu) {
                    this.menu[k] = state;
                }
            },

            toggleUrlsAll() {
                const state = this.$el.checked;
                for (let k in this.urls) {
                    this.urls[k] = state;
                }
            },

            toggleDashAll() {
                const state = this.$el.checked;
                for (let k in this.dash) {
                    this.dash[k] = state;
                }
            },

            toggleExtraAll() {
                const state = this.$el.checked;
                for (let k in this.extra) {
                    this.extra[k] = state;
                }
            },

            match(element) {
                const etext = element.innerText.toLowerCase();
                const text = Alpine.store("search").search;
                const fields = text.toLowerCase().split(" ");
                for (let f of fields) {
                    if (etext.indexOf(f) == -1) {
                        return false;
                    }
                }
                return true;
            },
        };
    });
});
