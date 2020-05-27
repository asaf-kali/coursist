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

/*** Init ***/

$(document).ready(function () {
    initHandlebars();
});