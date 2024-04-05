$(document).ready(function () {
  
   var collaps = $('[id*="collapse"]');
  for(var i=0;i<collaps.length;i++){
     var id = collaps.eq(i).attr('id').replace('collapse','');
     var quill = new Quill("#editor"+id, {
    theme: "snow",
  });
  var answer = $("#answer" + id).val()
  if(answer){
    quill.root.innerHTML = answer
  }
  //quill.on('text-change', function(delta, oldDelta, source) {
    // console.log(quill.root.innerHTML)
    //console.log(quill);
    //console.log($(this));
    //var quillObj = $(this).prev('.ql-editor').get(0).quill;   
    //console.log(quillObj);
    //console.log($(e.target));
   // console.log(event.target);
   
   
    //var faq_id = quill.container.id.replace('editor','');
    //$("#answer" + faq_id).val(quill.root.innerHTML);
    //console.log(quill, faq_id);
    //console.log($("#answer" + faq_id).val())
    //if (source == 'api') {
      //console.log("An API call triggered this change.");
    //} else if (source == 'user') {
     // console.log("A user action triggered this change.");
   // }
  //});
  }
  var quills = document.querySelectorAll('[id*="editor"]');
  quills.forEach(function(quill) {
  var q = Quill.find(quill);
  q.on('text-change', function(delta, oldDelta, source) {
    var faq_id = q.container.id.replace('editor','');
    console.log(faq_id);
    $("#answer" + faq_id).val(q.root.innerHTML);
    //console.log(containerElement);
  });
});
});
