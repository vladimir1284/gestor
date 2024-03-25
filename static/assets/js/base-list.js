let tables = document.getElementsByTagName("tbody");
window.onload = function() {
    let add = document.getElementsByClassName("add")[0];
    if (add.style.visibility != "hidden") {
        $(add).tooltip("show");
    }
};
function filterTag(tagName) {
    let i, j;

    let title_tag = document.getElementById("filter_tag");
    if (tagName == "all") {
        title_tag.innerHTML = "";
        let search = document.getElementById("search");
        search.value = "";
    } else {
        title_tag.innerHTML = "(" + tagName + ")";
    }
    let tables = document.getElementsByTagName("tbody");
    for (j = 0; j < tables.length; j++) {
        let tr = tables[j].getElementsByTagName("tr");
        for (i = 0; i < tr.length; i++) {
            if (tr[i].dataset["tag"] == tagName || tagName == "all") {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
let grids = document.getElementsByTagName("table");
for (let j = 0; j < tables.length; j++) {
    const g = grids[j];
    const ths = g.querySelectorAll("th");
    ths.forEach((e) => {
        if (!e.dataset.type) return;

        const o = document.createElement("i");
        o.classList.add("sortable");
        o.classList.add("text-secondary");
        // o.classList.add("float-end");
        o.classList.add("bx");
        o.classList.add("bx-sort-alt-2");
        e.prepend(o);
        // e.appendChild(o);
    });
    g.onclick = (e) => {
        if (e.target.tagName != "TH") return;

        let th = e.target;
        if (!th.dataset.type) return;
        // if TH, then sort
        // cellIndex is the number of th:
        //   0 for the first column
        //   1 for the second column, etc
        const tableElement = th.closest("table");

        const ths = g.querySelectorAll("th");
        ths.forEach((e) => {
            const o = e.querySelector(".order");
            if (o) e.removeChild(o);

            if (e === th) {
                return;
            }
            const sortable = e.querySelector(".sortable");
            if (sortable) sortable.style.display = "";
            e.dataset.order = 0;
        });

        // Get the tbody element associated with the table
        const tbodyElement = tableElement.querySelector("tbody");

        const r = sortGrid(tbodyElement, th, th.cellIndex, th.dataset.type);

        if (r == 1) {
            const o = document.createElement("i");
            o.classList.add("order");
            // o.classList.add("float-end");
            o.classList.add("bx");
            o.classList.add("text-primary");
            if (th.dataset.reversed == 1) o.classList.add("bx-sort-up");
            else o.classList.add("bx-sort-down");
            th.prepend(o);
            // th.appendChild(o);
            const sortable = th.querySelector(".sortable");
            sortable.style.display = "none";
            th.dataset.order = 1;
        }
    };
}

function sortGrid(tbody, th, colNum, type) {
    let rowsArray = Array.from(tbody.rows);

    // compare(a, b) compares two rows, need for sorting
    let compare;

    let reversed = 0;

    switch (type) {
        case "amount":
            reversed = 1;
            compare = function(rowA, rowB) {
                return (
                    rowA.cells[colNum].innerHTML.replace("$", "") -
                    rowB.cells[colNum].innerHTML.replace("$", "")
                );
            };
            break;
        case "days":
            reversed = 1;
            compare = function(rowA, rowB) {
                const d =
                    rowA.cells[colNum].dataset.days - rowB.cells[colNum].dataset.days;
                if (d == 0) return 1;
                return d;
            };
            break;
        case "number":
            compare = function(rowA, rowB) {
                return rowA.cells[colNum].innerHTML - rowB.cells[colNum].innerHTML;
            };
            break;
        case "string":
            compare = function(rowA, rowB) {
                return rowA.cells[colNum].innerHTML > rowB.cells[colNum].innerHTML
                    ? 1
                    : -1;
            };
            break;
        case "custom-string":
            compare = function(rowA, rowB) {
                return rowA.cells[colNum].dataset["custom"] >
                    rowB.cells[colNum].dataset["custom"]
                    ? 1
                    : -1;
            };
            break;
        default:
            return 0;
    }

    if (th.dataset.order == 1) {
        reversed = 1 - th.dataset.reversed;
    }
    th.dataset.reversed = reversed;

    // sort
    rowsArray.sort(compare);
    if (reversed == 1) {
        console.log("reversed");
        let reversedArray = rowsArray.reverse();
        tbody.append(...reversedArray);
    } else {
        console.log("normal");
        tbody.append(...rowsArray);
    }

    return 1;
}
