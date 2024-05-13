


const ext_sum = document.querySelector("#ext_t");
const abs_sum = document.querySelector("#abs_t");
const extractive = document.querySelector("#extractive")
const abstractive = document.querySelector("#abstractive")
let temp=0 ;
function summary(){
    if(ext_sum.innerHTML==""){
        extractive.style.display="none"
    }
    if(abs_sum.innerHTML==""){
        abstractive.style.display="none"
    }
}

summary();
const textS = document.querySelector("#textS")
const Spain = document.querySelector(".spain")

function spain(){

    if (textS.innerHTML!=null && temp===0){
        Spain.style.cssText=`  display: block;
        width: 40px !important;
        height: 40px !important;
    
    
      
        border-radius: 50%;
        border: 5px solid #e91e63;
        transform: rotate(1turn);
        transition: transform 3s;
        border-left-color:transparent ;

        
        `
    
    }
    else{
        Spain.style.display=`  display: none;
        width: 40px !important;
        height: 40px !important;
        
        
        
        border-radius: 50%;
        border: 5px solid #e91e63;
        transform: rotate(1turn);
        transition: transform 3s;
        border-left-color:transparent ;
       
    `
    }
    temp=1
}

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
