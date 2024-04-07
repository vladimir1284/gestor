function filter(from, showNum, filter) {
    const map = {};
    filter = filter.toLowerCase();

    let num = 0;
    for (let [name, elements] of Object.entries(from)) {
        if (name.toLowerCase().indexOf(filter) != -1) {
            map[name] = elements;
            num++;
            continue;
        }
        for (let element of elements) {
            if (element.date.toLowerCase().indexOf(filter) != -1) {
                if (map[name]) {
                    map[name].push(element);
                    num++;
                } else {
                    map[name] = [element];
                    num++;
                }
            }
        }
        if (showNum > 0 && num >= showNum) break;
    }

    return map;
}

function expand(e, tableId) {
    const data = CSS.escape(e.getAttribute("data"));
    const rowspan = e.getAttribute("data-rowspan");
    const hidden = e.getAttribute("rowspan") == 1;

    if (hidden) {
        e.setAttribute("rowspan", rowspan);
    } else {
        e.setAttribute("rowspan", 1);
    }

    const trs = document.querySelectorAll(`#${tableId} tr[data="${data}"]`);

    trs.forEach((tr) => {
        if (hidden) {
            tr.style.display = "";
            return;
        }
        tr.style.display = "none";
    });
}

function renderTable(from, tableId, expanded) {
    const body = document.querySelector(`#${tableId} tbody`);
    body.innerHTML = "";

    for (let [name, elements] of Object.entries(from)) {
        for (let [index, element] of elements.entries()) {
            const tr = document.createElement("tr");
            body.appendChild(tr);
            if (index != 0) {
                tr.setAttribute("data", name);
                if (!expanded) tr.style.display = "none";
            } else {
                const nameTD = document.createElement("td");
                tr.appendChild(nameTD);
                nameTD.classList.add("pointer");
                nameTD.setAttribute("data", name);
                nameTD.setAttribute("data-rowspan", elements.length);

                if (expanded) nameTD.setAttribute("rowspan", elements.length);
                else nameTD.setAttribute("rowspan", 1);

                nameTD.onclick = () => {
                    expand(nameTD, tableId);
                };

                if (elements.length > 1) {
                    nameTD.innerHTML = `${name} <span class="float-end">[${elements.length}]</span>`;
                } else {
                    nameTD.innerHTML = name;
                }
            }

            const date = document.createElement("td");
            tr.appendChild(date);
            const adate = document.createElement("a");
            date.appendChild(adate);
            adate.href = element.url;
            adate.innerText = element.date;

            const price = document.createElement("td");
            tr.appendChild(price);
            price.innerText = element.price;
        }
    }
}
