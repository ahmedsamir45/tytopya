function deleteText(textId) {
    fetch("/deletetext", {
        method: "POST",
        body: JSON.stringify({ textId: textId })
    }).then((_res) => {
        window.location.href = "/dashboard"
    })
}
function deleteMessage(mId) {
    fetch("/deletemessage", {
        method: "POST",
        body: JSON.stringify({ mId: mId })
    }).then((_res) => {
        window.location.href = "/dashboard"
    })
}

function deletePDFChat(chatId) {
    fetch("/delete-pdf-chat", {
        method: "POST",
        body: JSON.stringify({ chatId: chatId })
    }).then((_res) => {
        window.location.href = "/dashboard"
    })
}