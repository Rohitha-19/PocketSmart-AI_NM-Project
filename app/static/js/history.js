function historyDetails(row){
 const request=row.request||{};
 if(row.planner==="home"){
  const items=(request.items||[]).map(item=>`${item.quantity} × ${item.category}`).join(", ");
  return [request.rooms?.length?`Rooms: ${request.rooms.join(", ")}`:"",items?`Items: ${items}`:"",request.special_requirements||""].filter(Boolean).join(" · ");
 }
 if(row.planner==="party"){
  const needs=(request.needs||[]).join(", ");
  return [`${request.guests||0} guests`,request.event_type,request.venue_type?`Venue: ${request.venue_type}`:"",needs?`Needs: ${needs}`:"",request.special_requests||""].filter(Boolean).join(" · ");
 }
 return [request.occasion,request.style_preferences||request.style,request.image_uploaded?"Outfit image included":"No outfit image"].filter(Boolean).join(" · ");
}
function historyRecommendations(row){
 const recommendations=row.result.recommendations||[];
 if(!recommendations.length)return "<p class=\"empty-state\">No item recommendations were saved.</p>";
 return `<div class="saved-items">${recommendations.map(item=>`<article class="saved-item"><div><span class="history-tag">${escapeHtml(item.category)}</span><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.reason)}</p></div><div class="saved-item-price"><strong>${money(item.estimated_price)}</strong><a href="${safeUrl(item.url)}" target="_blank" rel="noopener">${escapeHtml(item.platform)} ↗</a></div></article>`).join("")}</div>`;
}
(async()=>{
 if(!requireAuth())return;
 const list=document.getElementById("historyList");
 try{
  const rows=await api("/api/history");
  list.innerHTML=rows.length?rows.map(row=>{
   const remaining=Math.max(0,Number(row.result.budget)-Number(row.result.allocated_total));
   const title=`${row.planner[0].toUpperCase()+row.planner.slice(1)} Budget Planner`;
    const tipTitle=row.planner==="jewelry"?"Styling Tips":"Additional suggestions";
    return `<article class="history-record"><header class="history-record-head"><div><span class="history-tag ${escapeHtml(row.planner)}">${escapeHtml(title)}</span><time>${new Date(row.created_at).toLocaleString()}</time></div><p>${escapeHtml(row.result.summary)}</p></header><div class="activity-amounts"><span>Total budget <strong>${money(row.result.budget)}</strong></span><span>Remaining <strong>${money(remaining)}</strong></span></div><p class="history-context">${escapeHtml(historyDetails(row))}</p><details><summary>View full details</summary>${historyRecommendations(row)}<section class="saved-tips"><h3>${tipTitle}</h3><ul>${(row.result.tips||[]).map(tip=>`<li>${escapeHtml(tip)}</li>`).join("")}</ul></section></details></article>`
  }).join(""):"<p class=\"empty-state\">No recommendations saved yet. Choose a planner to create your first plan.</p>";
 }catch(error){list.innerHTML=`<p class=\"error\">${escapeHtml(error.message)}</p>`}
})();