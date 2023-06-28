var f = document.getElementById("file");
var send = document.getElementById("send")
var message = document.getElementById("message")
var attachments = document.getElementsByClassName("messagebox__attachments")[0]

var request = new XMLHttpRequest();
var data = new FormData();
var files = [];



f.onchange = (event) => {
    var file = event.target.files[0];
    files.push(file);

    var fr = new FileReader()
    fr.onload = event => {
        var img = new Image();
        img.src = event.target.result;
        attachments.appendChild(img)
    }
    fr.readAsDataURL(file)

}

send.onclick = (event) => {
    if (files.length > 0)
        data.append("attachment", files[0])
    if (message.value)
        data.append("message", message.value)
    if (files.length > 0 || message.value) {
        request.open("POST", "/api/thread.answer");
        request.send(data);
    }
    
    data = new FormData()
    files = []
    message.value = ""
    f.value = ""
    attachments.innerHTML = ""
}
