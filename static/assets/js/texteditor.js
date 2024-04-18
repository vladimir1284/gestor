const save = () => {
    const form = document.querySelector("#form");
    const text_input = document.querySelector('input[name="text"]');
    text_input.value = editor.getHTMLCode();
    form.submit();
    return false;
};

const editor = new RichTextEditor("#editor", {
    editorResizeMode: "none",
    toolbarfactory_save: (cmd, suffix) => {
        console.log(cmd, suffix);
        var btn = document.createElement("button");
        btn.innerHTML = `
            <svg viewBox="-2 -2 36 36" fill="#5F6368" style="width: 100%; height: 100%; margin: 0px; border: 0px; align-self: self-start;"><path d="M27.71,9.29l-5-5A1,1,0,0,0,22,4H6A2,2,0,0,0,4,6V26a2,2,0,0,0,2,2H26a2,2,0,0,0,2-2V10A1,1,0,0,0,27.71,9.29ZM12,6h8v4H12Zm8,20H12V18h8Zm2,0V18a2,2,0,0,0-2-2H12a2,2,0,0,0-2,2v8H6V6h4v4a2,2,0,0,0,2,2h8a2,2,0,0,0,2-2V6.41l4,4V26Z"></path></svg>
        `;
        btn.className = "btn";
        btn.style.cssText = "height:32px;margin:2px;padding:0px 5px";
        btn.onclick = save;
        return btn;
    },

    toolbarfactory_vars: function(cmd, suffix) {
        var editor = this; //Use this, maybe editor2 variable is not ready yet.
        var option = {};
        var inp;
        option.fillinput = function(input) {
            inp = input;
            inp.innerText = "VAR";
            inp.style.overflowX = "hidden";
        };
        option.fillpanel = function(panel) {
            // var sel = document.createElement("select");
            // sel.style.cssText = "height:32px;margin:2px;padding:0px 5px";
            // function addOption(text, value) {
            //     var option = document.createElement("option");
            //     option.innerText = text;
            //     option.setAttribute("value", value);
            //     option.rawValue = value;
            //     sel.appendChild(option);
            // }
            // addOption("Select an item...");
            // addOption("Red title", "red");
            // addOption("Blue content", "blue");
            // sel.onclick = function(e) {
            //     //the select will get focus , editor will lost focus
            //     e.stopPropagation(); //prevent editor get focus automatically
            // };
            // sel.onchange = function() {
            //     var option = sel.options[sel.selectedIndex];
            //     var val = option.rawValue;
            //     sel.selectedIndex = 0;
            //     editor3.insertHTML(
            //         "<span style='color:" + val + "'>You selected " + val + "</span>",
            //     );
            // };
            //
            panel.style.padding = "0";

            VARS.forEach((v) => {
                const opt = document.createElement("button");
                opt.className = "border-bottom btn btn-link";
                opt.innerHTML = `${v.pattern}`;
                opt.onclick = () => {
                    editor.closeCurrentPopup();
                    editor.insertHTML(v.pattern);
                };
                panel.appendChild(opt);
            });
        };

        var btn = editor.createToolbarDropDown(option, cmd, suffix);
        return btn;
    },

    toolbar: "towit",
    toolbarMobil: "towit",
    toolbar_towit:
        "{removeformat,find,selectall}" +
        "|{ucase,lcase,lineheight}" +
        "|{insertblockquote,insertunorderedlist,insertorderedlist,indent,outdent}" +
        "|{inserttable,insertimage,insertlink,inserthorizontalrule,insertdate,insertchars}" +
        "|{vars}" +
        "#{newdoc,save,preview,print,code}" +
        "-{paragraphs,fontname,fontsize}" +
        "|{forecolor,backcolor}" +
        "|{bold,italic,underline,strike,superscript,subscript}" +
        "|{justifyleft,justifycenter,justifyright,justifyfull}" +
        "#{undo,redo,fullscreenenter,fullscreenexit}",
});

const Head = `
    <meta charset="utf-8" />
    <base href="http://localhost:8000/erp/template/template-edit/1">
    <link id="url-css-content" rel="stylesheet" href="/richtexteditor/runtime/richtexteditor_content.css">
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500;1,600;1,700&amp;display=swap" rel="stylesheet">
    <!-- Icons. Uncomment required icon fonts -->
    <link rel="stylesheet" href="/static/assets/vendor/fonts/boxicons.css">
    <!-- Core CSS -->
    <link rel="stylesheet" href="/static/assets/vendor/css/core.css" class="template-customizer-core-css">
    <link rel="stylesheet" href="/static/assets/vendor/css/theme-default.css" class="template-customizer-theme-css">
    <link rel="stylesheet" href="/static/assets/css/demo.css">
    <!-- Vendors CSS -->
    <link rel="stylesheet" href="/static/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css">
    <link rel="stylesheet" href="/static/assets/vendor/libs/apex-charts/apex-charts.css">
    <!-- Page CSS -->
    <style>
        body {
            overflow: hidden;
            margin: 0;
            padding: 0;
            background: white;
        }
    </style>
  </head>
`;
const iframe = document.querySelector("iframe");
iframe.contentDocument.head.innerHTML = Head;
