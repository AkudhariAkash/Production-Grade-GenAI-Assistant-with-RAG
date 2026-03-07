let sessionId = localStorage.getItem("sessionId")

if(!sessionId){
sessionId = Math.random().toString(36).substring(7)
localStorage.setItem("sessionId",sessionId)
}

async function sendMessage(){

const input = document.getElementById("user-input")
const message = input.value.trim()

if(!message) return

addMessage("User",message,"user")

input.value=""

const loading = addMessage("Assistant","Typing...","bot")

const response = await fetch("/api/chat",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
sessionId:sessionId,
message:message
})

})

const data = await response.json()

loading.innerHTML = "<b>Assistant:</b> "+data.reply

}

function addMessage(sender,text,cls){

const messages = document.getElementById("messages")

const div = document.createElement("div")

div.className="message "+cls

div.innerHTML="<b>"+sender+":</b> "+text

messages.appendChild(div)

messages.scrollTop = messages.scrollHeight

return div

}

function handleKey(event){

if(event.key === "Enter"){
sendMessage()
}

}