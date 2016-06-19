function Site() {
    // Make a call to the api.
    this.api = function(action, data, callback){
        var baseURL = document.location.origin + "/api/1/";
        $.post(
            baseURL + action,
            data,
            callback
        );
    }

    // make a call to a plugins api
    this.plugin_api = function(plugin, action, data, callback) {
        var baseURL = document.location.origin + "/api/plugin/";
        $.post(
            baseURL + [plugin, action].join("/"),
            data,
            callback
        );
    }

    // Turns an element filled with markdown into HTML
    this.markdown = function(id){
        var md = new showdown.Converter();
        var text = $(id).text();
        $(id).html(md.makeHtml(text));
    }
    this.route = function(path){
        document.querySelector('app-router').go(path);
    }
    // Adds content to a modal notification.
    // title: the title string
    // text: The html contents of the modal
    // buttons: a list of buttons
    // button[0]: button text
    // button[1]: button colour
    // button[2]: button click callback
    this.notify = function(title, text, buttons){
        $('#notify-modal .modal-footer').empty();
        for (var i in buttons) {
            var button = buttons[i];
            $('#notify-modal .modal-footer').append(
                $('<a/>')
                    .addClass('waves-effect')
                    .addClass('waves-light')
                    .addClass('btn')
                    .addClass(button[1])
                    .text(button[0])
                    .click(button[2])
            );
        }
        $('#notify-modal .modal-content').empty();
        $('#notify-modal .modal-content').append(
            $('<h3/>')
                .text(title),
            $('<p/>')
                .html(text)
        );
    }
    this.modal_open = false;
    this.notify_toggle = function(){
        if (this.modal_open){
            $('#notify-modal').closeModal();
            this.modal_open = false;
        }
        else {
            $('#notify-modal').openModal();
            this.modal_open = true;
        }
    }
    this.toast = function(msg) {
      console.warn("site.toast is deprecated for something that hasn't been created yet. Use `x` instead when it's done.");
      console.log(msg);
    }
    // Adds callback to the end of the JS execution flow. Useful for running
    // parallel to ayncronous code with no callback
    this.append_stack = function(callback, num){
        if (typeof num != 'undefined' && num > 0){
            this.append_stack(function(){
                setTimeout(callback, 0);
            }, num - 1);
        }
        else {
            setTimeout(callback, 0);
        }
    }
}
window.$$ = document.querySelector;
var site = new Site();
