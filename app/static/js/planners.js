function setStatus(text,error=false){const el=document.getElementById("status");if(el){el.textContent=text;el.className="message"+(error?" error":"")}}
function initHomePlanner(){
 if(!requireAuth())return;document.getElementById("homeForm").addEventListener("submit",async e=>{e.preventDefault();setStatus("Generating...");
    const f=new FormData(e.target);const specialRequirements=f.get("special_requirements").trim();
    const items=[["Lighting",f.get("lights")],["Ceiling Fans",f.get("fans")],["Furniture",f.get("furniture")],["Dining Tables",f.get("tables")]]
     .map(([category,quantity])=>({category,quantity:Number(quantity),notes:specialRequirements})).filter(item=>item.quantity>0);
    const data={budget:Number(f.get("budget")),rooms:f.getAll("rooms"),items,special_requirements:specialRequirements};
    try{renderResult(await api("/api/generate-home",{method:"POST",body:JSON.stringify(data)}),{rooms:data.rooms});setStatus("Plan ready.")}catch(err){setStatus(err.message,true)}
 })
}
function initPartyPlanner(){
 if(!requireAuth())return;document.getElementById("partyForm").addEventListener("submit",async e=>{e.preventDefault();setStatus("Generating...");
    const f=new FormData(e.target);const data={budget:Number(f.get("budget")),guests:Number(f.get("guests")),event_type:f.get("event_type"),venue_type:f.get("venue_type"),venue_preference:f.get("venue_type"),needs:f.getAll("needs"),special_requests:f.get("special_requests").trim()};
    try{renderResult(await api("/api/generate-party",{method:"POST",body:JSON.stringify(data)}),data);setStatus("Plan ready.")}catch(err){setStatus(err.message,true)}
 })
}
function initJewelryPlanner(){
 if(!requireAuth())return;document.getElementById("jewelryForm").addEventListener("submit",async e=>{e.preventDefault();setStatus("Generating...");
    const form=new FormData(e.target);const imageInput=document.getElementById("outfitImage");
    if(!imageInput.files.length)form.delete("image");
    const context={occasion:form.get("occasion"),stylePreferences:form.get("style_preferences"),imageUploaded:imageInput.files.length>0};
    try{const data=await api("/api/generate-jewelry",{method:"POST",headers:{"Authorization":"Bearer "+getToken()},body:form});renderResult(data,context);setStatus("Plan ready.")}catch(err){setStatus(err.message,true)}
 })
 const input=document.getElementById("outfitImage"),preview=document.getElementById("outfitPreview"),previewWrap=document.getElementById("outfitPreviewWrap"),remove=document.getElementById("removeImage");
 let previewUrl="";
 const clearPreview=()=>{if(previewUrl)URL.revokeObjectURL(previewUrl);previewUrl="";preview.removeAttribute("src");previewWrap.hidden=true};
 input.addEventListener("change",()=>{
  const file=input.files && input.files[0];
  if(!file)return;
  if(previewUrl)URL.revokeObjectURL(previewUrl);
  previewUrl=URL.createObjectURL(file);
  preview.src=previewUrl;
  previewWrap.hidden=false;
  setStatus("Image selected. Submit to generate your jewelry styling plan.");
 });
 remove.addEventListener("click",()=>{
  input.value="";
  clearPreview();
  setStatus("Outfit image removed.");
 });
}
