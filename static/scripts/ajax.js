const CSRF_KEY = 'csrfmiddlewaretoken';


function logAndCall(response, callback, comment) {
    console.debug(`Ajax response (${comment}): ${JSON.stringify(response)}`);
    if (callback)
        callback(response);
}


function ajax(data, success, error, csrfToken = undefined, url = undefined) {
    if (!url) {
        url = location.href.replace(location.search, '');
        console.log(`Posting to: ${url}`);
    }
    if (!(CSRF_KEY in data)) {
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

function onReady(bind) {
    $(document).ready((e) => bind(e));
}

function bindInput(inputId, success, error, csrfToken, url = undefined) {
    onReady(() => {
        $("#" + inputId).on("input", (e) => {
            ajax({value: $(e.target).val()}, success, error, csrfToken, url);
        });
    });
}

function bindButton(btnId, dataGetter, success, error, csrfToken, url = undefined) {
    onReady(() => {
        $("#" + btnId).click((e) => {
            const data = dataGetter(e);
            ajax(data, success, error, csrfToken, url);
        });
    });
}

// Not baked yet
// function formAjax(e, form, url, success, error) {
//     e.preventDefault();
//     const data = $(form).serialize();
//     ajax(data, url, success, error);
// }
