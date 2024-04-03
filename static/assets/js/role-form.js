function getState(elements) {
    let mark = false;
    let unmark = false;
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].checked) {
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

function setState(input, elements) {
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
}

function setOnUpdate(input, elements) {
    for (let i = 0; i < elements.length; i++) {
        elements[i].onchange = () => {
            setState(input, elements);
        };
    }
}

function setChecked(elements, checked) {
    for (let i = 0; i < elements.length; i++) {
        elements[i].checked = checked;
    }
}

function setOnMark(input, elements) {
    input.onchange = () => {
        setChecked(elements, input.checked);
    };
}

function init() {
    const items = document.querySelectorAll(".accordion-item");
    for (let i = 0; i < items.length; i++) {
        const input = items[i].querySelector(
            '.accordion-header>input[type="checkbox"]'
        );
        if (input) {
            const elements = items[i].querySelectorAll(
                '.accordion-body .controls .checkbox input[type="checkbox"]'
            );
            setState(input, elements);
            setOnUpdate(input, elements);
            setOnMark(input, elements);
        }
    }
}

window.addEventListener("load", init);
