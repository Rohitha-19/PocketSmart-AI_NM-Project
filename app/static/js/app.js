function getToken(){return localStorage.getItem("pocketsmart_token")}
function authHeaders(){const t=getToken(); return t ? {"Authorization":"Bearer "+t} : {}}
function requireAuth(){if(!getToken()){location.href="/login"; return false} return true}
function logout(){localStorage.removeItem("pocketsmart_token"); localStorage.removeItem("pocketsmart_user"); location.href="/"}
document.addEventListener("DOMContentLoaded",()=>{const link=document.getElementById("authLink"); if(link && getToken()){link.textContent="Logout";link.href="#";link.onclick=(e)=>{e.preventDefault();logout()}}})
function money(v){return new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:0}).format(v)}
function renderResult(data,context={}){
 const box=document.getElementById("results"); if(!box)return;
 const remaining=Math.max(0,Number(data.budget)-Number(data.allocated_total));
 const categories=[...new Set(data.recommendations.map(item=>item.category))];
 const tipTitle=data.planner==="jewelry"?"Styling Tips":"Additional Suggestions";
 const recommendationSource=data.ai_used?"Gemini-powered recommendations":data.ai_status==="unavailable"?"Gemini unavailable · catalog fallback":"Catalog recommendations";
 const sections=categories.map(category=>{const items=data.recommendations.filter(item=>item.category===category);const allocation=items.reduce((total,item)=>total+Number(item.estimated_price||0)*Number(item.quantity||1),0);return `<section class="result-category"><header><div><h3>${escapeHtml(category)}</h3><p>Allocation: ${money(allocation)}</p></div></header><div class="result-table-wrap"><table class="result-table"><thead><tr><th>Item</th><th>Description</th><th>Price</th><th>Quantity</th><th>Shopping link</th></tr></thead><tbody>${items.map(item=>`<tr><td><strong>${escapeHtml(item.title)}</strong></td><td>${escapeHtml(item.reason)}</td><td>${money(item.estimated_price)}</td><td>${Number(item.quantity||1)}</td><td><a class="store-link" href="${safeUrl(item.url)}" target="_blank" rel="noopener">${escapeHtml(item.platform)} ↗</a></td></tr>`).join("")}</tbody></table></div></section>`}).join("");
 const outfit=context.occasion?`<section class="result-category outfit-analysis"><header><div><h3>Outfit Analysis</h3><p>${escapeHtml(context.occasion)}${context.stylePreferences?` · ${escapeHtml(context.stylePreferences)}`:""}</p></div></header><p>${context.imageUploaded?"Outfit image included for coordination.":"No outfit image added."}</p></section>`:"";
 const rooms=context.rooms?.length?`<p class="result-context">Rooms: ${context.rooms.map(escapeHtml).join(", ")}</p>`:"";
 box.innerHTML=`<section class="result-plan"><div class="result-title"><div><p class="eyebrow">YOUR ${escapeHtml(data.planner)} BUDGET PLAN</p><h2>${data.planner==="jewelry"?"Your Personalized Jewelry Recommendations":"Your Personalized Budget Plan"}</h2><p>${escapeHtml(data.summary)}</p></div><span class="pill">${recommendationSource}</span></div><section class="budget-summary"><h3>Budget Summary</h3><div><p>Total Budget <strong>${money(data.budget)}</strong></p><p>Remaining Budget <strong class="remaining">${money(remaining)}</strong></p></div></section>${rooms}${outfit}<div class="result-categories">${sections||"<p>No recommendations matched these selections. Try increasing the budget or selecting more needs.</p>"}</div><section class="suggestions"><h3>${tipTitle}</h3><ul>${data.tips.map(item=>`<li>${escapeHtml(item)}</li>`).join("")}</ul></section></section>`;
}
function escapeHtml(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c]))}
function safeUrl(u){try{const x=new URL(u); return ["https:","http:"].includes(x.protocol)?x.href:"#"}catch{return "#"}}
async function api(url, options={}){
 const headers={...authHeaders(),...(options.headers||{})};
 const isForm=options.body instanceof FormData;
 if(!isForm && options.body && !headers["Content-Type"]) headers["Content-Type"]="application/json";
 const res=await fetch(url,{...options,headers});
 let data={};try{data=await res.json()}catch{}
 if(!res.ok)throw new Error(data.detail||"Request failed");
 return data
}
