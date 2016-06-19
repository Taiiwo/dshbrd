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
    this.route = function(path){
        document.querySelector('app-router').go(path, {replace: true});
    }
    this.toast = function(msg) {
        document.querySelector("#toast").show({text: msg, duration: 3000})
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
