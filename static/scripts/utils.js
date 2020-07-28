/*** Frontend Templates ***/

let hb_templates = {};

function initHandlebars() {
    const allScripts = $("[type='text/x-handlebars-template']");
    Array.from(allScripts).forEach(script => {
        const name = script.attributes.name.nodeValue;
        const source = script.innerHTML;
        hb_templates[name] = Handlebars.compile(source);
    });
}


/*** Fading ***/

const refreshRate = 25;
const fadeOutSpeed = 200;
const fadeInSpeed = 200;
let isFading = new Map();

function hide(id, after = undefined) {
    if (isFading.get(id)) {
        setTimeout(hide, refreshRate, id, after);
        return;
    }
    isFading.set(id, true);
    console.log(`Fading out ${id}`);
    $(`#${id}`).fadeOut(fadeOutSpeed, () => {
        console.log(`Fading out ${id} done`);
        isFading.set(id, false);
        if (after)
            after();
    });
}

function show(id, before = undefined, after = undefined) {
    if (isFading.get(id)) {
        setTimeout(show, refreshRate, id, before, after);
        return;
    }
    if (before)
        before();
    isFading.set(id, true);
    console.log(`Fading in ${id}`);
    $(`#${id}`).fadeIn(fadeInSpeed, () => {
        console.log(`Fading in ${id} done`);
        isFading.set(id, false);
        if (after)
            after();
    });
}

let TOAST_COUNT = 0;


function showToast(toast) {
    toast.id = TOAST_COUNT++;
    // message.bg = message.tag === "error" ? "danger" : message.tag;
    // switch (message.tag) {
    //     case "error":
    //         message.fa_class = "times";
    //         break;
    //     case "warning":
    //         message.fa_class = "exclamation";
    //         break;
    //     case "success":
    //         message.fa_class = "check";
    //         break;
    //     default:
    //         message.fa_class = "info";
    //         break;
    // }
    if (!toast.delay) toast.delay = 5000;
    const html = hb_templates["toast-message"]({"message": toast});
    $("#toasts-container").prepend(html);
    $(`#toast-${toast.id}`).toast("show");
}

/*** Init ***/

$(document).ready(function () {
    initHandlebars();
});