var header = document.getElementsByClassName("header")[0];
var body = document.body;
var doc = document.documentElement;

var title = document.getElementsByClassName("title")[0];
var description = document.getElementsByClassName("description")[0];

window.onscroll = () => {
    if (doc.scrollTop > 50) {
        header.style.height = `50px`
        description.style.display = "none"
        title.style.fontSize = "30px"
        title.style.color = "white"
        header.style.backgroundColor = "#0C151C"
    } else {
        header.style.height = `200px`
        description.style.display = "inherit"
        title.style.fontSize = "50px"
        title.style.color = "#363636"
        header.style.backgroundColor = "transparent"
    }
}