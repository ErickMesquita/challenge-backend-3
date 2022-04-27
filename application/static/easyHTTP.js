// Author: thacker_shahid (@thacker_shahid)
// Source: https://www.geeksforgeeks.org/difference-between-put-and-delete-request-in-vanilla-javascript/


function easyHTTP() {

    // Initialising new XMLHttpRequest method.
    this.http = new XMLHttpRequest();
}

// Make an HTTP Delete Request
easyHTTP.prototype.delete = function (url, callback) {

    // Open an object (GET/POST, PATH,
    // ASYNC-TRUE/FALSE)
    this.http.open('DELETE', url, true);

    // Assigning this to self to have
    // scope of this into the function
    let self = this;

    // When the response is ready
    this.http.onload = function () {

        // Checking status
        if (self.http.status === 200) {

            // Callback function(Error, response text)
            callback(null, 'Post Deleted');
        } else {

            // Callback function (Error message)
            callback('Error: ' + self.http.status);
        }
    }

    // Send the request
    this.http.send();
}

function delete_user_by_id(user_id){
    // Instantiating easyHTTP
    const http = new easyHTTP;
    let url = window.location.href + "/" + user_id.toString();
    let callback = function (err, response) {
        if (err) {
            console.log(err);
        } else {
            console.log(response);
        }
    });
    http.delete(url, callback)
}



// Delete prototype method(URL,
// callback(error,response text))
http.delete(
    'https://jsonplaceholder.typicode.com/posts/1',
    function (err, response) {
        if (err) {
            console.log(err);
        } else {
            console.log(response);
        }
    });