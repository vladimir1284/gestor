var Editor = null;

const save = () => {
  const form = document.querySelector("#form");
  form.submit();
};

const insertText = (text) => {
  Editor.model.change((writer) => {
    writer.insertText(text, Editor.model.document.selection.getFirstPosition());
  });
};

const watchdog = new CKSource.EditorWatchdog();

window.watchdog = watchdog;

watchdog.setCreator((element, config) => {
  return CKSource.Editor.create(element, config).then((editor) => {
    Editor = editor;
    return editor;
  });
});

watchdog.setDestructor((editor) => {
  return editor.destroy();
});

watchdog.on("error", handleSampleError);

watchdog
  .create(document.querySelector("#id_text"), {
    removePlugins: ["Title"],
    toolbar: {
      items: [
        "undo",
        "redo",
        "findAndReplace",
        "selectAll",
        // "|",
        // "textPartLanguage",
        "|",
        "blockQuote",
        "bulletedList",
        "numberedList",
        "todoList",
        "outdent",
        "indent",
        "|",
        "insertTable",
        "imageInsert",
        "link",
        "specialCharacters",
        "horizontalLine",
        "codeBlock",
        "code",
        "pageBreak",
        "|",
        "showBlocks",
        "htmlEmbed",
        "sourceEditing",
        "-",
        "heading",
        // "style",
        "|",
        "fontFamily",
        "fontSize",
        "fontColor",
        "fontBackgroundColor",
        "highlight",
        "removeFormat",
        "|",
        "alignment",
        "bold",
        "italic",
        "underline",
        "strikethrough",
        "superscript",
      ],
      shouldNotGroupWhenFull: true,
    },
    heading: {
      options: [
        { model: "paragraph", title: "Paragraph" },
        { model: "heading1", view: "h1", title: "Heading 1" },
        { model: "heading2", view: "h2", title: "Heading 2" },
        { model: "heading3", view: "h3", title: "Heading 3" },
        { model: "heading4", view: "h4", title: "Heading 4" },
        { model: "heading5", view: "h5", title: "Heading 5" },
        { model: "heading6", view: "h6", title: "Heading 6" },
      ],
    },
  })
  .catch(handleSampleError);

function handleSampleError(error) {
  const issueUrl = "https://github.com/ckeditor/ckeditor5/issues";

  const message = [
    "Oops, something went wrong!",
    `Please, report the following error on ${issueUrl} with the build id "w8ifvduz8vjy-ojtpqoe2mafb" and the error stack trace:`,
  ].join("\n");

  console.error(message);
  console.error(error);
}
