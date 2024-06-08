function deleteText(textId){
    fetch("/deletetext",{
        method:"POST",
        body: JSON.stringify({textId:textId})
    }).then((_res)=>{
        window.location.href = "/dashboard"
    })
}