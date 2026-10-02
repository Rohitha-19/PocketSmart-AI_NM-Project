async function submitAuth(formId, endpoint){
 const form=document.getElementById(formId); if(!form)return;
 form.addEventListener("submit",async e=>{
  e.preventDefault(); const msg=document.getElementById("formMessage"); msg.textContent="Working..."; msg.className="message";
  const body=Object.fromEntries(new FormData(form).entries());
  if(formId==="registerForm" && body.password!==body.confirm_password){msg.textContent="Passwords do not match.";msg.className="message error";return}
  try{const data=await fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}).then(async r=>{const d=await r.json();if(!r.ok)throw new Error(d.detail||"Request failed");return d});
    localStorage.setItem("pocketsmart_token",data.token);localStorage.setItem("pocketsmart_user",JSON.stringify(data.user));location.href="/dashboard";
  }catch(err){msg.textContent=err.message;msg.className="message error"}
 })
}
submitAuth("loginForm","/api/login"); submitAuth("registerForm","/api/register");
const forgotPasswordLink=document.getElementById("forgotPasswordLink");
forgotPasswordLink?.addEventListener("click",event=>{event.preventDefault();const msg=document.getElementById("formMessage");msg.textContent="Password recovery is not configured for this local app.";msg.className="message"});
