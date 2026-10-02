(async()=>{
 if(!requireAuth())return;
 try{
  const user=await api("/api/me");document.getElementById("welcome").textContent=`Hi ${user.name}. Choose a planner or review your recent plans.`;
    const rows=await api("/api/history");document.getElementById("count").textContent=`${rows.length} saved plan${rows.length===1?"":"s"}`;
    document.getElementById("history").innerHTML=rows.length?rows.slice(0,3).map(r=>{const title=`${r.planner[0].toUpperCase()+r.planner.slice(1)} Budget Planner`;const remaining=Math.max(0,Number(r.result.budget)-Number(r.result.allocated_total));return `<article class="activity-card"><div class="activity-card-head"><strong>${escapeHtml(title)}</strong><time>${new Date(r.created_at).toLocaleDateString()}</time></div><p>${escapeHtml(r.result.summary)}</p><div class="activity-amounts"><span>Budget <strong>${money(r.result.budget)}</strong></span><span>Remaining <strong>${money(remaining)}</strong></span></div><a class="btn primary" href="/history">View full details</a></article>`}).join(""):"<p class=\"empty-state\">No recommendations yet. Choose a planner above to get started.</p>";
 }catch(e){document.getElementById("history").innerHTML=`<p class="error">${escapeHtml(e.message)}</p>`}
})()
