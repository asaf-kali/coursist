const CSRF_KEY = 'csrfmiddlewaretoken';
let CSRF_TOKEN = '';

function logAndCall(response, callback, comment) {
    console.debug(`Ajax response (${comment}): ${JSON.stringify(response)}`);
    if (callback)
        callback(response);
}

function ajax(data, success = undefined, error = undefined, csrfToken = undefined, url = undefined) {
    if (!url) {
        url = location.href.replace(location.search, '');
        console.log(`Posting to: ${url}`);
    }
    if (!data) {
        console.log("Empty data, aborting ajax request");
        return
    }
    if (!(CSRF_KEY in data)) {
        if (!csrfToken)
            csrfToken = CSRF_TOKEN;
        data[CSRF_KEY] = csrfToken;
    }
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: function (response) {
            logAndCall(response, success, "success");
        },
        error: function (response) {
            logAndCall(response, error, "error");
        }
    });
}

function bindInput(inputId, success = undefined, error = undefined, csrfToken = undefined, url = undefined) {
    onReady(() => {
        $("#" + inputId).on("input", (e) => {
            ajax({value: $(e.target).val()}, success, error, csrfToken, url);
        });
    });
}

function bindButton(btnId, dataGetter, success = undefined, error = undefined, csrfToken = undefined, url = undefined) {
    onReady(() => {
        $("#" + btnId).click((e) => {
            const data = dataGetter(e);
            ajax(data, success, error, csrfToken, url);
        });
    });
}
