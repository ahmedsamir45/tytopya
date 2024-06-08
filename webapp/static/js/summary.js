
// ###############get the elements ##########
const ext_sum = document.querySelector("#ext_t");
const abs_sum = document.querySelector("#abs_t");
const extractive = document.querySelector("#extractive")
const abstractive = document.querySelector("#abstractive")
let temp=0 ;

// ##############  summary function #############
// ext_sum.addEventListener("load",function(){
//     if (this.innerHTML!='undefined'){
//         extractive.classList.add("active")
//     }
//     else{
//         extractive.classList.remove("active")
//     }
// })
// abs_sum.addEventListener("load",function(){
//     if (this.innerHTML!='undefined'){
//         abstractive.classList.add("active")
//     }
//     else{
//         abstractive.classList.remove("active")
//     }
// })

function EXTsummary(){
    if(ext_sum.innerHTML=="undefined"||ext_sum.innerHTML==undefined){
        ext_sum.innerHTML =""
    }
    if(ext_sum.innerHTML!=""){
        extractive.classList.add("active")
    }
    else{
        extractive.classList.remove("active")
    }
 
}
function ABSsummary(){
    if(abs_sum.innerHTML=="undefined"||abs_sum.innerHTML==undefined){
        abs_sum.innerHTML =""
    }
    if(abs_sum.innerHTML!=""){
        abstractive.classList.add("active")
    }
    else{
        abstractive.classList.remove("active")
    }
}
ABSsummary()
EXTsummary()





// ########### spain loop function ###################
const textS = document.getElementById("textS")
const Spain = document.querySelector(".spain")
let textFild 
const button = document.getElementById("btext");


textS.addEventListener(("input"),function(){
    if (this.value !=""){
        button.classList.add("activeAnimation")
    } 
    else{
        button.classList.remove("activeAnimation")
    }

})





button.addEventListener("click",function(){
    if (textS.value != ""){
        Spain.classList.add("active")
        extractive.classList.remove("active")
        abstractive.classList.remove("active")
    }
    else{
        Spain.classList.remove("active")
        extractive.classList.add("active")
        abstractive.classList.add("active")
    }
})

// textS.addEventListener("input",function(){
//     extractive.classList.add("active")
//     abstractive.classList.add("active")
// })



///////////// copy function ///////////////////////////
const copiedText = document.getElementById('abs_t');
const textToCopy = document.getElementById('click1');

textToCopy.addEventListener('click', () => {


    // Create a textarea element to hold the text
    const textarea = document.createElement('textarea');
    textarea.textContent = copiedText.textContent;
    document.body.appendChild(textarea);

    // Select the text in the textarea
    textarea.select();
    textarea.setSelectionRange(0, 99999); // For mobile devices

    // Copy the selected text to the clipboard
    document.execCommand('copy');

    // Remove the textarea from the DOM
    document.body.removeChild(textarea);


});
const copiedText2 = document.getElementById('ext_t');
const textToCopy2 = document.getElementById('click2');

textToCopy2.addEventListener('click', () => {
   
  

    // Create a textarea element to hold the text
    const textarea = document.createElement('textarea');
    textarea.textContent = copiedText2.textContent;
    document.body.appendChild(textarea);

    // Select the text in the textarea
    textarea.select();
    textarea.setSelectionRange(0, 99999); // For mobile devices

    // Copy the selected text to the clipboard
    document.execCommand('copy');

    // Remove the textarea from the DOM
    document.body.removeChild(textarea);


});











//////////////typing effect functions ////////////////////////
var myText1 = abs_sum.textContent

let temp2=0

 function typing1(){
    abs_sum.textContent=""
    var typeWriter=setInterval(function(){
        document.getElementById("abs_t").textContent += myText1[temp2];
        temp2++;
        if(temp2>=myText1.length-1){
            clearInterval(typeWriter);}
    },25)

}
if (myText1 != null){
    typing1()
}
var myText2 = ext_sum.textContent

let temp3=0

 function typing2(){
    ext_sum.textContent=""
    var typeWriter2=setInterval(function(){
        document.getElementById("ext_t").textContent += myText2[temp3];
        temp3++;
        if(temp3>=myText2.length-1){
            clearInterval(typeWriter2);}
    },25)

}
if (myText2 != null){
    typing2()
}


