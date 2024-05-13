const text2 = "Welcome to TyTopya!"; // Text to be typed


let index2 = 0;

function type2() {
    document.getElementById("typed-text2").textContent = text2.slice(0, index2);
    index2++;
    if (index2 > text2.length) {
        index2 = 0;
    }
    setTimeout(type2, 150);
}


type2();